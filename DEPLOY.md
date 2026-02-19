# Quick Deployment Guide

## 🚀 Deploy to Vercel in 3 Steps

### Step 1: Prepare Your Project

```bash
cd "c:\Users\pc\Desktop\boot cin"
```

### Step 2: Install Vercel CLI

```bash
npm i -g vercel
```

If you don't have Node.js, download it from: https://nodejs.org/

### Step 3: Deploy

```bash
vercel login
vercel
```

That's it! Your API will be live at: `https://your-project.vercel.app`

---

## 📝 After Deployment

1. **Test your API:**
   - Visit: `https://your-project.vercel.app`
   - Use the `/extract` endpoint to upload CIN images

2. **Update test.html:**
   - Open `test.html` in a browser
   - Change API endpoint to your Vercel URL
   - Upload a CIN image to test

3. **Optional - Add Google Cloud Vision:**
   - For better OCR accuracy (see README.md)
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Add `GOOGLE_APPLICATION_CREDENTIALS` with your JSON key

---

## 🔧 Alternative: Deploy via GitHub

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

2. **Connect to Vercel:**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Click "Deploy"

---

## 📱 Test Your Deployed API

### Using cURL:
```bash
curl -X POST "https://your-project.vercel.app/extract" -F "file=@cin-image.jpg"
```

### Using Python:
```python
import requests
response = requests.post(
    "https://your-project.vercel.app/extract",
    files={"file": open("cin-image.jpg", "rb")}
)
print(response.json())
```

---

## ❓ Common Issues

**Problem:** "Command not found: vercel"
- **Solution:** Install Node.js first, then run `npm i -g vercel`

**Problem:** "No token found"
- **Solution:** Run `vercel login` first

**Problem:** OCR returns empty results
- **Solution:** Add Google Cloud Vision API credentials (see README.md)

---

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed configuration
- Add Google Cloud Vision for better accuracy
- Customize OCR logic in `api/ocr_processor.py`
- Add authentication and rate limiting for production

## 🆘 Need Help?

- Check [README.md](README.md) for detailed documentation
- Visit Vercel docs: https://vercel.com/docs
- Open an issue on GitHub

---

**Your Morocco CIN OCR API is ready! 🎉**
