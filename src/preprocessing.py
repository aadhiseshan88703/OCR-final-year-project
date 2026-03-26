import cv2

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # Simple resize only - no other processing to test if OCR works
    image = cv2.resize(image, (1024, 1024))

    return image
