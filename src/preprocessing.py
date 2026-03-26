import cv2

def preprocess_image(image_path):
    image = cv2.imread(image_path)

    # Resize (standard size)
    image = cv2.resize(image, (1024, 1024))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    # Thresholding
    _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)

    return thresh
