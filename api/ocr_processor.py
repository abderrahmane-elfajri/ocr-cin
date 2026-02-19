import os
from PIL import Image
import re
from typing import Dict, Optional, Any
try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from google.cloud import vision
    import io
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False


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


def process_with_tesseract(image: Image.Image) -> Dict[str, Optional[Any]]:
    """Process CIN image using Tesseract OCR."""
    if not TESSERACT_AVAILABLE:
        raise Exception("Tesseract OCR is not available. Install pytesseract.")
    
    result = create_empty_result()
    
    # Extract text with both French and Arabic
    text_fr = pytesseract.image_to_string(image, lang='fra')
    text_ar = pytesseract.image_to_string(image, lang='ara')
    combined_text = text_fr + "\n" + text_ar
    
    # Detect side
    result["side"] = detect_side(combined_text)
    
    # Extract CIN number
    result["cin_number"] = extract_cin_number(text_fr)
    
    # Extract date of birth
    result["date_of_birth"] = extract_date(text_fr)
    
    # Note: For production, you would need more sophisticated parsing
    # to extract names, places, and addresses accurately from the OCR text
    # This requires pattern matching, field position detection, or ML models
    
    return result


def process_with_google_vision(image: Image.Image) -> Dict[str, Optional[Any]]:
    """Process CIN image using Google Cloud Vision API."""
    if not GOOGLE_VISION_AVAILABLE:
        raise Exception("Google Cloud Vision is not available.")
    
    result = create_empty_result()
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
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
    
    return result


def process_cin_image(image: Image.Image) -> Dict[str, Optional[Any]]:
    """
    Main function to process CIN image.
    Uses Google Vision if available, falls back to Tesseract.
    """
    try:
        # Try Google Vision first if credentials are available
        if GOOGLE_VISION_AVAILABLE and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return process_with_google_vision(image)
        elif TESSERACT_AVAILABLE:
            return process_with_tesseract(image)
        else:
            # Fallback: return empty structure
            result = create_empty_result()
            result["side"] = "FRONT"  # Default guess
            return result
    
    except Exception as e:
        # Return empty structure on error
        result = create_empty_result()
        return result
