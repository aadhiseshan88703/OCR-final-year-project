import json
import os

def postprocess(texts, boxes, confidences):
    """
    Cleans extracted text and formats the output into structured JSON.
    """
    cleaned_texts = [t.strip() for t in texts]
    
    formatted_data = {
        "text": cleaned_texts,
        "boxes": boxes,
        "confidence": confidences
    }
    return formatted_data

def save_json(data, path="output/result.json"):
    """
    Saves the structured data to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
