import os
import sys

from src.pipeline import process_document
from src.postprocessing import save_json

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


def list_images(folder):
    """Return all image paths found inside the folder."""
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    images = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
            images.append(path)
    if not images:
        raise FileNotFoundError(f"No image file found in folder: {folder}")
    return images


if __name__ == "__main__":
    folder = "sample_data"
    lang = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        image_paths = list_images(folder)
    except FileNotFoundError as ex:
        print(f"Error: {ex}")
        sys.exit(1)

    print("Starting OCR Invoice System")
    print(f"Processing {len(image_paths)} image(s) from: {folder}")
    if lang:
        print(f"Forcing OCR language: {lang}")

    for image_path in image_paths:
        print(f"Processing image: {image_path}")
        try:
            result = process_document(image_path, lang=lang)
            print(f"Pipeline result: {len(result['text'])} texts found")

            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join("output", f"{base_name}.json")
            saved_path = save_json(result, path=output_path)
            print(f"Results saved to {saved_path}")
        except Exception as e:
            print(f"Pipeline failed for {image_path}: {e}")

    print("OCR processing completed successfully")
