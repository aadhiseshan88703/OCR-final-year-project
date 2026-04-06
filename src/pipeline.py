from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr
from src.postprocessing import postprocess


def process_document(image_path, lang=None):
    """
    Defines the full OCR pipeline: preprocessing -> OCR -> postprocessing.

    lang: Optional PaddleOCR language key or name. If omitted, uses automatic
    multi-language OCR merging to keep the best text per region.
    """
    print("Step 1: Preprocessing image...")
    preprocessed = preprocess_image(image_path)

    print("Step 2: Running OCR...")
    texts, boxes, confidences, ocr_metadata = run_ocr(preprocessed, lang=lang)

    print("Step 3: Postprocessing results...")
    result = postprocess(texts, boxes, confidences, ocr_metadata=ocr_metadata)

    return result
