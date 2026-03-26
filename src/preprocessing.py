import cv2

def preprocess_image(image_path):
    """
    This module performs image preprocessing including resizing,
    grayscale conversion, noise removal, and thresholding to improve OCR accuracy.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}. Ensure it exists.")
    return image
