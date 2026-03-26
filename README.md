# OCR Invoice System

A Python-based Optical Character Recognition (OCR) system for extracting text from invoice images. Supports English, Tamil, and Hindi languages.

## Project Structure

```
ocr-invoice-system/
│
├── src/
│   ├── preprocessing.py      # Image preprocessing (resize, grayscale, denoise, threshold)
│   ├── ocr_engine.py         # PaddleOCR engine for text extraction
│   ├── postprocessing.py     # Text cleaning and JSON output formatting
│   ├── pipeline.py           # Complete OCR pipeline orchestration
│
├── sample_data/
│   └── sample_invoice.jpg    # Sample invoice image for testing
│
├── output/
│   └── result.json           # OCR output in JSON format
│
├── main.py                   # Entry point script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Module Descriptions

### preprocessing.py
Performs image preprocessing including:
- Resizing to standard dimensions (1024x1024)
- Grayscale conversion
- Gaussian blur for noise removal
- Binary thresholding for improved OCR accuracy

### ocr_engine.py
Uses PaddleOCR for text extraction:
- Supports multilingual OCR (English, Tamil, Hindi)
- Extracts text, bounding boxes, and confidence scores
- Returns structured data for downstream processing

### postprocessing.py
Processes OCR results:
- Cleans extracted text (whitespace removal)
- Removes duplicates
- Formats output into structured JSON
- Saves results to file

### pipeline.py
Orchestrates the complete workflow:
- Preprocessing → OCR → Postprocessing
- Handles inter-module communication

### main.py
Entry point that:
- Runs the pipeline on sample invoice
- Saves structured output to JSON

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The script will:
1. Read the sample invoice from `sample_data/sample_invoice.jpg`
2. Process it through the OCR pipeline
3. Save the results to `output/result.json`

## Output Format

```json
{
  "text": ["ABC Store", "Total 500"],
  "boxes": [
    [[10,20],[100,20],[100,40],[10,40]],
    [[15,60],[120,60],[120,90],[15,90]]
  ],
  "confidence": [0.98, 0.95]
}
```

## Requirements

- paddleocr
- paddlepaddle
- opencv-python
- numpy
- Pillow

## Notes

- Add your invoice images to the `sample_data/` folder
- Modify the `lang` parameter in `ocr_engine.py` to switch languages:
  - `'en'` for English
  - `'ta'` for Tamil
  - `'hi'` for Hindi

## GitHub Commit & Push Commands

Use this section to track and push the current code to your GitHub repo:

```bash
# 1. Check repository status
cd "c:\Users\ELCOT\Desktop\New project\ocr-invoice-system"
git status

# 2. Add changed files
git add .

# 3. Commit changes
git commit -m "Fix OCR pipeline, enforce real OCR path, disable MKLDNN/oneDNN, update README"

# 4. Push to GitHub remote
git push origin main   

# Optional: check last commit
git log --oneline -3
```

> Repo URL:
> https://github.com/aadhiseshan88703/OCR-final-year-project.git
