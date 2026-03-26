from src.pipeline import process_document
from src.postprocessing import save_json

if __name__ == "__main__":
    image_path = "sample_data/sample_invoice.jpg"

    result = process_document(image_path)

    save_json(result)

    print("✅ OCR processing completed. Output saved!")
