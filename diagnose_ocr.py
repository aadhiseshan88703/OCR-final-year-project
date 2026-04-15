import cv2
import numpy as np
from src.ocr_engine import _get_model, AUTO_LANGUAGES
from paddleocr.tools.infer.utility import get_rotate_crop_image

path = 'sample_data/Gujarati.png'
img = cv2.imread(path)
print('img_exists', img is not None)
if img is None:
    raise SystemExit(1)
for lang in AUTO_LANGUAGES:
    try:
        print('---', lang)
        ocr = _get_model(lang)
        res = ocr.ocr(img, cls=False, rec=False)
        boxes = res[0] if res and res[0] else []
        print('boxes', len(boxes))
        if boxes:
            crop = get_rotate_crop_image(img, np.array(boxes[0], dtype=np.float32))
            rec = ocr.ocr(crop, det=False, cls=False)
            print('sample', rec)
    except Exception as exc:
        print('ERROR', lang, exc)
