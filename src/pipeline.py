from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr
from src.postprocessing import postprocess

def process_document(image_path):
    """
    Defines the full OCR pipeline: preprocessing -> OCR -> postprocessing.
    """
    print("📷 Step 1: Preprocessing image...")
    preprocessed = preprocess_image(image_path)
    
    print("🔤 Step 2: Running OCR...")
    texts, boxes, confidences = run_ocr(preprocessed)
    
    print("📝 Step 3: Postprocessing results...")
    result = postprocess(texts, boxes, confidences)
    
    return result
