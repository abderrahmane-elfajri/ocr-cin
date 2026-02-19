import os
from PIL import Image
import re
from typing import Dict, Optional, Any
import io as iostream

try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


def create_empty_result() -> Dict[str, Optional[Any]]:
    """Create empty CIN result structure."""
    return {
        "side": None,
        "cin_number": None,
        "first_name_fr": None,
        "last_name_fr": None,
        "first_name_ar": None,
        "last_name_ar": None,
        "date_of_birth": None,
        "place_of_birth_fr": None,
        "place_of_birth_ar": None,
        "father_name_fr": None,
        "mother_name_fr": None,
        "father_name_ar": None,
        "mother_name_ar": None,
        "address_fr": None,
        "address_ar": None
    }


def detect_side(text: str) -> str:
    """Detect if the CIN card is FRONT or BACK side."""
    text_lower = text.lower()
    
    # Front side indicators
    front_keywords = ['date de naissance', 'date of birth', 'lieu de naissance', 
                      'né(e) le', 'ne(e) le', 'carte nationale']
    
    # Back side indicators
    back_keywords = ['père', 'pere', 'mère', 'mere', 'mother', 'father', 
                     'adresse', 'address', 'nom du père', 'nom de la mère']
    
    front_count = sum(1 for keyword in front_keywords if keyword in text_lower)
    back_count = sum(1 for keyword in back_keywords if keyword in text_lower)
    
    if back_count > front_count:
        return "BACK"
    else:
        return "FRONT"


def extract_cin_number(text: str) -> Optional[str]:
    """Extract CIN number (format: 1-2 letters + 6-7 digits)."""
    patterns = [
        r'\b([A-Z]{1,2}\d{6,7})\b',
        r'\bN[°o]?\s*:?\s*([A-Z]{1,2}\d{6,7})\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    return None


def extract_date(text: str) -> Optional[str]:
    """Extract date in format DD/MM/YYYY or DD-MM-YYYY."""
    patterns = [
        r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        r'\b(\d{1,2}\s+(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+\d{4})\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def parse_mrz(text: str) -> Dict[str, Optional[str]]:
    """Parse MRZ (Machine Readable Zone) from CIN card."""
    result = {}
    
    # Clean text - remove extra spaces and newlines
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # CIN MRZ format (TD1 format - 3 lines):
    # Line 1: IDMAR... (Document code + Country + Name)
    # Line 2: CIN number + DOB + Sex + Expiry + Nationality
    # Line 3: Additional data
    
    # Try to find CIN number from MRZ (format: letter(s) + digits)
    cin_pattern = r'([A-Z]{1,2}\d{6,7})'
    cin_match = re.search(cin_pattern, text)
    if cin_match:
        result['cin_number'] = cin_match.group(1)
    
    # Try to find date of birth (YYMMDD format in MRZ)
    dob_pattern = r'(\d{6})[0-9M]'  # 6 digits followed by sex marker
    dob_matches = re.findall(dob_pattern, text)
    for dob in dob_matches:
        # Convert YYMMDD to DD/MM/YYYY
        if len(dob) == 6:
            yy, mm, dd = dob[0:2], dob[2:4], dob[4:6]
            # Assume 20xx for years > 26, 19xx otherwise
            yyyy = f"19{yy}" if int(yy) > 26 else f"20{yy}"
            result['date_of_birth'] = f"{dd}/{mm}/{yyyy}"
            break
    
    # Extract names from MRZ (between << markers)
    name_pattern = r'([A-Z]+)<<([A-Z<]+)'
    name_match = re.search(name_pattern, text)
    if name_match:
        last_name = name_match.group(1).replace('<', ' ').strip()
        first_name = name_match.group(2).replace('<', ' ').strip()
        result['last_name_fr'] = last_name
        result['first_name_fr'] = first_name
    
    return result


def extract_with_easyocr(image: Image.Image) -> Dict[str, Optional[Any]]:
    """Process CIN image using EasyOCR."""
    if not EASYOCR_AVAILABLE:
        raise Exception("EasyOCR is not available.")
    
    result = create_empty_result()
    
    try:
        # Initialize EasyOCR reader (French and Arabic)
        reader = easyocr.Reader(['fr', 'ar', 'en'], gpu=False)
        
        # Convert PIL Image to numpy array
        import numpy as np
        img_array = np.array(image)
        
        # Perform OCR
        ocr_results = reader.readtext(img_array)
        
        # Combine all text
        full_text = ' '.join([text for (_, text, _) in ocr_results])
        
        # Detect side
        result["side"] = detect_side(full_text)
        
        # Extract CIN number
        result["cin_number"] = extract_cin_number(full_text)
        
        # Extract date of birth
        result["date_of_birth"] = extract_date(full_text)
        
        # Try to parse MRZ if present
        mrz_data = parse_mrz(full_text)
        for key, value in mrz_data.items():
            if value and not result.get(key):
                result[key] = value
        
        # Extract structured data based on position and keywords
        for bbox, text, conf in ocr_results:
            text_clean = text.strip()
            text_lower = text_clean.lower()
            
            # Look for specific field indicators
            if 'nom' in text_lower and 'prenom' not in text_lower:
                # Next text might be the last name
                continue
            elif 'prenom' in text_lower or 'prénom' in text_lower:
                # Next text might be the first name
                continue
            elif 'né' in text_lower or 'née' in text_lower:
                # Look for date near this
                date = extract_date(text_clean)
                if date and not result['date_of_birth']:
                    result['date_of_birth'] = date
            elif 'père' in text_lower or 'pere' in text_lower:
                # This indicates back side
                result['side'] = 'BACK'
            elif 'mère' in text_lower or 'mere' in text_lower:
                result['side'] = 'BACK'
    
    except Exception as e:
        print(f"EasyOCR error: {str(e)}")
    
    return result


def process_with_tesseract(image: Image.Image) -> Dict[str, Optional[Any]]:
    """Process CIN image using Tesseract OCR."""
    if not TESSERACT_AVAILABLE:
        raise Exception("Tesseract OCR is not available. Install pytesseract.")
    
    result = create_empty_result()
    
    # Extract text with both French and Arabic
    text_fr = pytesseract.image_to_string(image, lang='fra')
    text_ar = pytesseract.image_to_string(image, lang='ara')
    text_eng = pytesseract.image_to_string(image, lang='eng')  # For MRZ
    combined_text = text_fr + "\n" + text_ar + "\n" + text_eng
    
    # Detect side
    result["side"] = detect_side(combined_text)
    
    # Extract CIN number
    result["cin_number"] = extract_cin_number(combined_text)
    
    # Extract date of birth
    result["date_of_birth"] = extract_date(combined_text)
    
    # Try to parse MRZ
    mrz_data = parse_mrz(combined_text)
    for key, value in mrz_data.items():
        if value and not result.get(key):
            result[key] = value
    
    # Note: For production, you would need more sophisticated parsing
    # to extract names, places, and addresses accurately from the OCR text
    # This requires pattern matching, field position detection, or ML models
    
    return result


def process_with_google_vision(image: Image.Image) -> Dict[str, Optional[Any]]:
    """Process CIN imstream.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Initialize Google Vision client
    client = vision.ImageAnnotatorClient()
    vision_image = vision.Image(content=img_byte_arr)
    
    # Perform text detection
    response = client.text_detection(image=vision_image)
    texts = response.text_annotations
    
    if texts:
        full_text = texts[0].description
        
        # Detect side
        result["side"] = detect_side(full_text)
        
        # Extract CIN number
        result["cin_number"] = extract_cin_number(full_text)
        
        # Extract date of birth
        result["date_of_birth"] = extract_date(full_text)
        
        # Try to parse MRZ
        mrz_data = parse_mrz(full_text)
        for key, value in mrz_data.items():
            if value and not result.get(key):
                result[key] = value
        result["side"] = detect_side(full_text)
        
        # Extract CIN number
        result["cin_number"] = extract_cin_number(full_text)
        
        # Extract date of birth
        result["date_of_birth"] = extract_date(full_text)
    
    return result


def process_cin_image(image: Image.Image) -> Dict[str, Optional[Any]]:
    """
    Main function to process CIN image.
    Priority: Google Vision > EasyOCR > Tesseract > Fallback
    """
    try:
        # Try Google Vision first if credentials are available
        if GOOGLE_VISION_AVAILABLE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return process_with_google_vision(image)
        
        # Try EasyOCR (good for Arabic and French)
        elif EASYOCR_AVAILABLE:
            return extract_with_easyocr(image)
        
        # Try Tesseract
        elif TESSERACT_AVAILABLE:
            return process_with_tesseract(image)
        
        else:
            # Fallback: Basic image analysis without OCR
            result = create_empty_result()
            result["side"] = "FRONT"  # Default guess
            return result
    
    except Exception as e:
        # Return empty structure on error with side detection as FRONT
        print(f"OCR processing error: {str(e)}")
        result = create_empty_result()
        result["side"] = "FRONT"
        return result
