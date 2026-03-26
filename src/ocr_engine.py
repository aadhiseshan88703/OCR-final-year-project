import os
from paddleocr import PaddleOCR

# Avoid remote model host checks when local data already available
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# Choose whether to keep mock fallback for development testing.
# Set to False to enforce real OCR only and fail loudly if OCR engine fails.
USE_MOCK_FALLBACK = False

# Initialize OCR with robust settings. keep arguments minimal for compatibility:
try:
    ocr = PaddleOCR(
        lang='en',
        use_angle_cls=False
    )
    print("✅ PaddleOCR initialized successfully")
    USE_REAL_OCR = True
except Exception as e:
    print(f"⚠️ PaddleOCR initialization failed: {e}")
    ocr = None
    USE_REAL_OCR = False

    if not USE_MOCK_FALLBACK:
        raise
    print("🔄 Using mock OCR for testing")


def run_ocr(image):
    if USE_REAL_OCR and ocr is not None:
        try:
            print("🔍 Running real OCR on image...")
            result = ocr.ocr(image)
            print(f"📊 OCR result type: {type(result)}")
            print(f"📊 OCR result length: {len(result) if result else 0}")

            texts = []
            boxes = []
            confidences = []

            if result and result[0]:
                print(f"📝 Found {len(result[0])} text detections")
                for i, line in enumerate(result[0]):
                    if len(line) >= 2:
                        box = line[0]
                        text_info = line[1]
                        if isinstance(text_info, list) and len(text_info) >= 2:
                            text = text_info[0]
                            conf = text_info[1]
                        else:
                            text = str(text_info)
                            conf = 0.0

                        texts.append(text)
                        boxes.append(box)
                        confidences.append(conf)
                        print(f"  {i+1}. Text: '{text}' (conf: {conf:.2f})")
            else:
                print("⚠️ No text detected")
                if USE_MOCK_FALLBACK:
                    print("🔄 Falling back to mock data")
                    return get_mock_ocr_results()
                raise RuntimeError("No text detected by real OCR")

            print(f"✅ OCR completed. Found {len(texts)} text elements")
            return texts, boxes, confidences
        except Exception as e:
            print(f"❌ OCR processing failed: {e}")
            if USE_MOCK_FALLBACK:
                print("🔄 Using mock OCR fallback")
                return get_mock_ocr_results()
            raise
    else:
        if USE_MOCK_FALLBACK:
            print("🔄 Using mock OCR results for testing")
            return get_mock_ocr_results()
        raise RuntimeError("PaddleOCR is not initialized and mock fallback is disabled")

def get_mock_ocr_results():
    """Return sample OCR results for testing when real OCR fails"""
    texts = [
        "SAMPLE INVOICE",
        "ABC Electronics Store",
        "Invoice Number: INV-2026-001",
        "Date: March 26, 2026",
        "Laptop Computer",
        "1",
        "$1200.00",
        "$1200.00",
        "Wireless Mouse",
        "2",
        "$25.00",
        "$50.00",
        "GRAND TOTAL:",
        "$1250.00"
    ]

    # Create mock bounding boxes (simplified rectangles)
    boxes = []
    confidences = []
    y_pos = 100
    for i, text in enumerate(texts):
        # Create a simple bounding box
        box = [
            [50, y_pos],      # top-left
            [400, y_pos],     # top-right
            [400, y_pos+30],  # bottom-right
            [50, y_pos+30]    # bottom-left
        ]
        boxes.append(box)
        confidences.append(0.95)  # High confidence for mock data
        y_pos += 40

    print(f"🎭 Mock OCR: Generated {len(texts)} sample text detections")
    return texts, boxes, confidences
