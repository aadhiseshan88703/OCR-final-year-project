import os
# Prevent OpenMP crash on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from paddleocr import PaddleOCR
import logging
# Suppress paddleocr debugging spam
logging.getLogger("ppocr").setLevel(logging.ERROR)

# multilingual OCR
ocr = PaddleOCR(lang='en') # can change to 'ta', 'hi', or 'en'

def run_ocr(image):
    """
    Extracts text, bounding boxes, and confidences from the preprocessed image.
    """
    result = ocr.ocr(image)
    texts = []
    boxes = []
    confidences = []
    
    if result and result[0]:
        for line in result[0]:
            box = line[0]
            text_info = line[1]
            text = text_info[0]
            conf = float(text_info[1])
            texts.append(text)
            boxes.append(box)
            confidences.append(conf)
            
    return texts, boxes, confidences
