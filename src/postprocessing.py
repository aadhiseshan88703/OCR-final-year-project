import json

def postprocess(texts, boxes, confidences):
    cleaned_texts = [t.strip() for t in texts]

    data = {
        "text": cleaned_texts,
        "boxes": boxes,
        "confidence": confidences
    }

    return data


def save_json(data, path="output/result.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
