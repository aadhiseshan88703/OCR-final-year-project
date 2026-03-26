from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr
from src.postprocessing import postprocess

def process_document(image_path):
    preprocessed = preprocess_image(image_path)

    texts, boxes, confidences = run_ocr(preprocessed)

    result = postprocess(texts, boxes, confidences)

    return result
