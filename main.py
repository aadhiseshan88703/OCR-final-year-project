from src.pipeline import process_document
from src.postprocessing import save_json

if __name__ == "__main__":
    print("🚀 Starting OCR Invoice System")
    image_path = "sample_data/sample_invoice.jpg"
    print(f"📁 Processing image: {image_path}")

    try:
        result = process_document(image_path)
        print(f"📊 Pipeline result: {len(result.get('text', []))} texts found")

        save_json(result)
        print("💾 Results saved to output/result.json")

        print("✅ OCR processing completed successfully!")
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
