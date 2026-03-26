from paddleocr import PaddleOCR

# multilingual OCR
ocr = PaddleOCR(lang='en')  # can change to 'ta', 'hi', or 'en'

def run_ocr(image):
    result = ocr.ocr(image)

    texts = []
    boxes = []
    confidences = []

    for line in result[0]:
        box = line[0]
        text = line[1][0]
        conf = line[1][1]

        texts.append(text)
        boxes.append(box)
        confidences.append(conf)

    return texts, boxes, confidences
