from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
from PIL import Image
import json
from typing import Optional
from .ocr_processor import process_cin_image

app = FastAPI(title="Morocco CIN OCR API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Morocco CIN OCR API",
        "version": "1.0.0",
        "endpoints": {
            "/extract": "POST - Extract CIN data from image"
        }
    }

@app.post("/extract")
async def extract_cin_data(file: UploadFile = File(...)):
    """
    Extract data from Morocco CIN card image.
    Accepts: JPG, JPEG, PNG
    Returns: JSON with extracted fields
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process image with OCR
        result = process_cin_image(image)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
