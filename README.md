# Morocco CIN OCR API

Advanced OCR extraction system specialized in Morocco CIN (Carte d'Identité Nationale) cards.

## Features

- ✅ Detects FRONT or BACK side automatically
- ✅ Extracts all CIN fields (names, dates, addresses)
- ✅ Supports Arabic and French text
- ✅ REST API with FastAPI
- ✅ Serverless deployment ready
- ✅ Supports Google Cloud Vision API or Tesseract OCR

## API Endpoints

### `POST /extract`
Extract data from CIN card image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file - JPG, PNG)

**Response:**
```json
{
  "side": "FRONT",
  "cin_number": "AB123456",
  "first_name_fr": "Mohamed",
  "last_name_fr": "Alami",
  "first_name_ar": "محمد",
  "last_name_ar": "العلمي",
  "date_of_birth": "01/01/1990",
  "place_of_birth_fr": "Casablanca",
  "place_of_birth_ar": "الدار البيضاء",
  "father_name_fr": null,
  "mother_name_fr": null,
  "father_name_ar": null,
  "mother_name_ar": null,
  "address_fr": null,
  "address_ar": null
}
```

## Local Development

### Prerequisites
- Python 3.9+
- Tesseract OCR (optional) or Google Cloud Vision API credentials

### Install Tesseract (Optional)

**Windows:**
```powershell
choco install tesseract
```
Or download from: https://github.com/UB-Mannheim/tesseract/wiki

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-ara tesseract-ocr-fra
```

### Setup

1. **Clone or navigate to project:**
```bash
cd "c:\Users\pc\Desktop\boot cin"
```

2. **Create virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run locally:**
```bash
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

6. **Test the API:**
Open http://localhost:8000 in your browser

## Deploy to Vercel

### Option 1: Deploy with Vercel CLI

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy:**
```bash
vercel
```

4. **Deploy to production:**
```bash
vercel --prod
```

### Option 2: Deploy via GitHub

1. **Push code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/morocco-cin-ocr.git
git push -u origin main
```

2. **Connect to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel will auto-detect the configuration
   - Click "Deploy"

### Option 3: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Click "Add New" → "Project"
3. Import your Git repository or upload project folder
4. Vercel will detect `vercel.json` automatically
5. Click "Deploy"

## Google Cloud Vision Setup (Recommended)

For better OCR accuracy, use Google Cloud Vision API:

1. **Create a Google Cloud Project:**
   - Go to https://console.cloud.google.com
   - Create a new project

2. **Enable Vision API:**
   - Enable "Cloud Vision API" in your project

3. **Create Service Account:**
   - Go to IAM & Admin → Service Accounts
   - Create service account with "Cloud Vision API User" role
   - Download JSON key file

4. **Add to Vercel:**
   - Go to your Vercel project settings
   - Add environment variable:
     - Name: `GOOGLE_APPLICATION_CREDENTIALS`
     - Value: Paste the entire JSON content
   
   OR encode as base64:
   ```bash
   # Convert to base64
   cat service-account-key.json | base64
   ```
   - Add as `GOOGLE_CREDENTIALS_BASE64` in Vercel

5. **Redeploy:**
```bash
vercel --prod
```

## Testing the Deployed API

### Using cURL:
```bash
curl -X POST "https://your-app.vercel.app/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/cin-card.jpg"
```

### Using Python:
```python
import requests

url = "https://your-app.vercel.app/extract"
files = {"file": open("cin-card.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Using JavaScript:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://your-app.vercel.app/extract', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Project Structure

```
boot cin/
├── api/
│   ├── index.py          # FastAPI application
│   └── ocr_processor.py  # OCR processing logic
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Troubleshooting

### Vercel Deployment Issues

**Problem:** Build fails with "Module not found"
- Solution: Ensure all dependencies are in `requirements.txt`

**Problem:** OCR not working on Vercel
- Solution: Tesseract is not available in Vercel serverless functions. Use Google Cloud Vision API instead.

**Problem:** File upload fails
- Solution: Check file size. Vercel has a 4.5MB limit for serverless functions.

### Local Development Issues

**Problem:** Tesseract not found
- Solution: Install Tesseract and add to PATH, or set `TESSERACT_CMD` environment variable

**Problem:** Arabic text not recognized
- Solution: Install Arabic language data for Tesseract:
  ```bash
  # The installation includes ara.traineddata
  ```

## Limitations

- **Vercel Serverless**: 10-second execution timeout, 4.5MB payload limit
- **OCR Accuracy**: Depends on image quality and OCR engine
- **Field Extraction**: Basic pattern matching included. For production, consider training a custom ML model for better field extraction.

## Enhancements for Production

1. **Advanced Field Extraction:**
   - Implement ML-based text position detection
   - Use layout analysis for field identification
   - Train custom NER models for name/address extraction

2. **Image Preprocessing:**
   - Add image quality checks
   - Implement rotation correction
   - Add contrast and brightness adjustment

3. **Rate Limiting:**
   - Add API rate limiting
   - Implement authentication

4. **Monitoring:**
   - Add logging and error tracking
   - Implement analytics

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
