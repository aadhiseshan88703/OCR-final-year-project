from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr
from src.postprocessing import postprocess

def process_document(image_path):
    print(f"🔄 Starting OCR pipeline for: {image_path}")

    print("📷 Step 1: Preprocessing image...")
    preprocessed = preprocess_image(image_path)
    print(f"✅ Preprocessing complete. Image shape: {preprocessed.shape}")

    print("🔤 Step 2: Running OCR...")
    texts, boxes, confidences = run_ocr(preprocessed)

    print("📝 Step 3: Postprocessing results...")
    result = postprocess(texts, boxes, confidences)
    print(f"✅ Pipeline complete. Final result: {len(result['text'])} texts detected")

    return result
