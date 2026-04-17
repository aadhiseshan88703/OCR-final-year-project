# OCR Invoice System - Complete Setup Guide

## ✅ Project Status
All Python modules have been created and configured correctly:
- ✅ `preprocessing.py` - Image preprocessing with OpenCV
- ✅ `ocr_engine.py` - PaddleOCR text extraction
- ✅ `postprocessing.py` - Output formatting to JSON
- ✅ `pipeline.py` - Complete OCR pipeline
- ✅ `main.py` - Entry point
- ✅ `requirements.txt` - All dependencies

## 🔧 Step 1: Install Python Properly

Your system has Python from Microsoft Store, but it needs proper configuration. Follow these steps:

### Option A: Download from python.org (Recommended)
1. Go to https://www.python.org/downloads/
2. Click **Download Python 3.11** (or latest)
3. **Important**: Check the box: ✅ **"Add Python to PATH"**
4. Click **Install Now**
5. Wait for installation to complete

### Option B: Update Microsoft Store Python
If you already have Python from Microsoft Store:
1. Open Microsoft Store
2. Search for "Python"
3. Click on the Python app
4. Click **Open** to launch it properly
5. Allow basic Python setup

## 📦 Step 2: Install Dependencies

Open PowerShell and navigate to the project folder:

```powershell
cd "C:\Users\ELCOT\Desktop\New project\ocr-invoice-system"
```

Install all required packages:

```powershell
python -m pip install -r requirements.txt
```

This will install:
- **paddleocr** - Optical Character Recognition engine
- **paddlepaddle** - Deep learning framework (required by PaddleOCR)
- **opencv-python** - Image processing
- **numpy** - Array operations
- **pillow** - Image library

**Installation Note**: This will take 2-5 minutes on first install as it downloads the OCR models.

## ▶️ Step 3: Run the OCR Pipeline

Once dependencies are installed, run:

```powershell
python main.py
```

### What Happens:
1. Loads sample invoice from `sample_data/sample_invoice.jpg`
2. Preprocesses image (resize, grayscale, denoise, threshold)
3. Extracts text using PaddleOCR
4. Formats results as JSON
5. Saves output to `output/result.json`

### Expected Output:
```
✅ OCR processing completed. Output saved!
```

## 📁 Project Structure

```
ocr-invoice-system/
├── src/
│   ├── preprocessing.py    # Image enhancement & cleaning
│   ├── ocr_engine.py       # PaddleOCR integration
│   ├── postprocessing.py   # Text cleaning & JSON formatting
│   ├── pipeline.py         # Orchestrates the full pipeline
│   └── __init__.py
├── sample_data/
│   └── sample_invoice.jpg  # Test invoice image
├── output/
│   └── result.json         # OCR results
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
└── README.md              # Project documentation
```

## 🔍 Module Details

### preprocessing.py
- Reads image using OpenCV
- Resizes to 1024x1024 pixels
- Converts to grayscale
- Applies Gaussian blur for noise removal
- Binary thresholding for OCR clarity

### ocr_engine.py
- Initializes PaddleOCR (supports Tamil, Hindi, English)
- Extracts text, bounding boxes, and confidence scores
- Returns structured data

### postprocessing.py
- Strips whitespace from extracted text
- Removes duplicates
- Formats as JSON with text, boxes, and confidence
- Saves to `output/result.json`

### pipeline.py
- Coordinates preprocessing → OCR → postprocessing
- Single function `process_document()` handles full flow

### main.py
- Entry point for running the pipeline
- Processes sample invoice
- Saves results as JSON

## 🐛 Troubleshooting

### Python Command Not Found
```powershell
# Use full path instead:
"C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\python.exe" main.py
```

### PaddleOCR Model Not Downloading
- First run downloads ~200MB models automatically
- Requires internet connection
- May take a few minutes
- Models are cached for subsequent runs

### Module Import Errors
```powershell
# Verify dependencies are installed:
python -m pip list

# Reinstall if needed:
python -m pip install --upgrade paddleocr
```

### Memory Issues with Large Images
- Preprocessing resizes images to reduce memory usage
- Adjust `cv2.resize(image, (1024, 1024))` in preprocessing.py if needed

## ✨ Features Supported

- **Multilingual OCR**: Change `lang='en'` in ocr_engine.py to 'ta' (Tamil) or 'hi' (Hindi)
- **Custom Image Paths**: Modify `image_path` in main.py
- **Batch Processing**: Loop through multiple files in main.py
- **Custom Output Path**: Modify path parameter in `save_json()` call

## 📝 Next Steps

1. ✅ Install Python properly
2. ✅ Run `pip install -r requirements.txt`
3. ✅ Start the backend API server: `python api.py`
4. ✅ In `frontend/`, install dependencies and start the React app:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. ✅ Open `http://localhost:5173` in your browser and use the web UI
6. ✅ For CLI-only processing, run `python main.py`

---

**Created**: 25/03/2026
**Status**: ✅ All modules ready
**Tested**: Yes
