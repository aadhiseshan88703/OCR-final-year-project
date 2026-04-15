import cv2


def _resize_for_ocr(image, target_width=1200):
    height, width = image.shape[:2]
    if width < target_width:
        scale = target_width / width
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    elif width > 1600:
        scale = 1600 / width
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return image


def _telugu_enhanced_variant(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    enhanced = cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)
    return enhanced


def preprocess_image(image_path):
    """
    This module performs image preprocessing including resizing and noise reduction.

    The OCR engine now generates language-specific variants lazily to avoid
    extra computation when the target language is known or when the default
    image variant is sufficient.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}. Ensure it exists.")

    image = _resize_for_ocr(image)
    return {
        "default": image,
    }
