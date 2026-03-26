import os
import sys

# Ensure emojis display correctly in Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.pipeline import process_document
from src.postprocessing import save_json

if __name__ == "__main__":
    image_path = "sample_data/sample_invoice.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
    else:
        print("🚀 Starting OCR Invoice System")
        print(f"📁 Processing image: {image_path}")
        
        try:
            result = process_document(image_path)
            print(f"📊 Pipeline result: {len(result['text'])} texts found")
            
            save_json(result)
            print("💾 Results saved to output/result.json")
            print("✅ OCR processing completed successfully!")
        except Exception as e:
            print(f"❌ Pipeline Failed: {e}")
