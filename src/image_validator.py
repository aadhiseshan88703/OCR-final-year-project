"""
image_validator.py
------------------
Per-image clarity validation before OCR processing.

Checks performed (any single failure marks the image as unclear):
  1. Blurriness   – Laplacian variance below threshold
  2. Brightness   – Mean pixel value too dark or too bright (washed out)
  3. Contrast     – Standard deviation of pixel values too low
  4. Minimum size – Image too small to reliably OCR
  5. Text region  – No Canny edges detected (likely blank / corrupt scan)

All thresholds are intentionally conservative so that real-world invoice
scans, camera photos, and smartphone captures still pass.
"""

import cv2
import numpy as np

# ── Tunable thresholds ────────────────────────────────────────────────────────
BLUR_THRESHOLD        = 30.0   # Laplacian variance; below → too blurry
MIN_BRIGHTNESS        = 20.0   # Mean gray value; below → too dark
MAX_BRIGHTNESS        = 245.0  # Mean gray value; above → overexposed / blank
MIN_CONTRAST_STD      = 10.0   # Std-dev of gray values; below → flat/washed-out
MIN_WIDTH             = 80     # pixels; below → image is way too small
MIN_HEIGHT            = 80     # pixels; below → image is way too small
MIN_EDGE_DENSITY      = 0.005  # fraction of Canny edge pixels; below → no text
# ─────────────────────────────────────────────────────────────────────────────


def _load_gray(image_input):
    """
    Accept either:
      • a file path (str / bytes)
      • a BGR numpy array (as returned by cv2.imread)
      • a dict with a 'default' key (as returned by preprocess_image)
    Returns a uint8 grayscale numpy array, or raises ValueError.
    """
    if isinstance(image_input, dict):
        img = image_input.get("default")
    elif isinstance(image_input, np.ndarray):
        img = image_input
    else:
        img = cv2.imread(str(image_input))

    if img is None:
        raise ValueError(f"Could not read image: {image_input}")

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img  # already single-channel

    return gray


def validate_image_clarity(image_input):
    """
    Validate whether an image is clear enough for reliable OCR.

    Parameters
    ----------
    image_input : str | np.ndarray | dict
        File path, BGR numpy array, or preprocessing dict.

    Returns
    -------
    (is_clear: bool, reason: str | None)
        is_clear=True  → image is acceptable; proceed with OCR.
        is_clear=False → image fails quality check; reason describes why.
    """
    try:
        gray = _load_gray(image_input)
    except ValueError as exc:
        return False, str(exc)

    h, w = gray.shape

    # 1. Minimum size
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return False, (
            f"Image too small ({w}×{h} px); minimum is {MIN_WIDTH}×{MIN_HEIGHT} px."
        )

    # 2. Brightness checks
    mean_brightness = float(np.mean(gray))
    if mean_brightness < MIN_BRIGHTNESS:
        return False, (
            f"Image is too dark (mean brightness {mean_brightness:.1f}; "
            f"minimum is {MIN_BRIGHTNESS})."
        )
    if mean_brightness > MAX_BRIGHTNESS:
        return False, (
            f"Image is overexposed / too bright (mean brightness {mean_brightness:.1f}; "
            f"maximum is {MAX_BRIGHTNESS})."
        )

    # 3. Contrast check
    std_brightness = float(np.std(gray))
    if std_brightness < MIN_CONTRAST_STD:
        return False, (
            f"Image has insufficient contrast (std-dev {std_brightness:.1f}; "
            f"minimum is {MIN_CONTRAST_STD}). Likely blank or washed-out."
        )

    # 4. Blurriness check – Laplacian variance
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < BLUR_THRESHOLD:
        return False, (
            f"Image is too blurry (Laplacian variance {laplacian_var:.2f}; "
            f"minimum is {BLUR_THRESHOLD})."
        )

    # 5. Edge density check – proxy for presence of readable text
    edges = cv2.Canny(gray, threshold1=50, threshold2=150)
    edge_density = float(np.count_nonzero(edges)) / (w * h)
    if edge_density < MIN_EDGE_DENSITY:
        return False, (
            f"No readable text regions detected (edge density {edge_density:.4f}; "
            f"minimum is {MIN_EDGE_DENSITY}). Image may be blank or severely cropped."
        )

    return True, None
