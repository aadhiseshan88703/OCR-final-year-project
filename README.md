# OCR + VLM Based Invoice Processing System

## Description

A robust, production-ready Optical Character Recognition (OCR) and Vision Language Model (VLM) based system designed to extract, interpret, and structure text from invoice images. This project provides a complete pipeline from image preprocessing to intelligent text extraction, handling multiple languages and complex invoice structures dynamically.

## Features

- **Multi-Language Support:** Extracts English, Tamil, Hindi, Telugu, and Kannada intelligently.
- **Smart Text Detection:** Utilizes mathematically optimized OCR cropping, drastically speeding up text detection times by running detection logic only once across large images.
- **Structured JSON Output:** Formats unstructured invoice text into structured data fields.
- **Deterministic Processing:** Batch processing capability that enforces strict lexicographical order for reliable extraction limits.
- **Microservice Ready:** Built with a scalable architecture, making it ready to be deployed as a backend API for modern web applications.

## Tech Stack

- **Backend:** Python, FastAPI
- **OCR Engine:** PaddleOCR
- **Advanced Processing:** LayoutLM (for layout-aware NLP), VLM architectures
- **Frontend Integration:** React
- **Image Processing:** OpenCV, NumPy, Pillow

## Project Structure

```
ocr-invoice-system/
│
├── src/
│   ├── preprocessing.py      # Image preprocessing (resize, grayscale, denoise, threshold)
│   ├── ocr_engine.py         # Highly-optimized PaddleOCR engine for extraction
│   ├── postprocessing.py     # Text cleaning and layout reconstruction
│   ├── pipeline.py           # Unified pipeline handler
│
├── sample_data/              # Directory for raw input images
├── output/                   # Directory for structured JSON output and logs
├── main.py                   # Standard entry point script
├── process_sequential.py     # Sequence-based batch processing script
├── requirements.txt          # Python dependencies
└── README.md                 # Project Documentation
```

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your workspace. We recommend using a virtual environment.

### 2. Install Dependencies
Clone the repository and install the required modules using `pip`:

```bash
git clone https://github.com/aadhiseshan88703/OCR-final-year-project.git
cd OCR-final-year-project
pip install -r requirements.txt
```

> **Note:** If you are using Windows, ensure to install the corresponding PaddlePaddle compiled binaries depending on your CPU/GPU hardware.

## Usage Steps

### Single Image Processing
To run the OCR pipeline on a simple batch or evaluate the system functionality:
```bash
python main.py
```

### Batch Sequencing (Production)
To extract all images located inside the `sample_data/` directory sequentially and preserve their output dynamically inside `output/result.json`:

```bash
python process_sequential.py
```

The system will intelligently determine text locations, parse out invoice structures, reconstruct bounding box spacing mathematically, and dump it into cleanly formatted JSON arrays.
