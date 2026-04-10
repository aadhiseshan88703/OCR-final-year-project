import os
# Prevent OpenMP crash on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from paddleocr import PaddleOCR
import logging
import shutil
import tarfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
# Suppress paddleocr debugging spam
logging.getLogger("ppocr").setLevel(logging.ERROR)

ocr_models = {}

SUPPORTED_LANGUAGES = {
    'latin': 'Latin/English',
    'ta': 'Tamil',
    'hi': 'Hindi/Marathi/Devanagari',
    'devanagari': 'Hindi/Marathi/Devanagari',
    'te': 'Telugu',
    'kn': 'Kannada',
    'ka': 'Kannada',
    'ml': 'Malayalam',
}

SCRIPT_RANGES = {
    'latin': [(0x0041, 0x005A), (0x0061, 0x007A)],
    'ta': [(0x0B80, 0x0BFF)],
    'hi': [(0x0900, 0x097F)],
    'devanagari': [(0x0900, 0x097F)],
    'kn': [(0x0C80, 0x0CFF)],
    'ka': [(0x0C80, 0x0CFF)],
    'te': [(0x0C00, 0x0C7F)],
    'ml': [(0x0D00, 0x0D7F)],
}

LANGUAGE_CODES = {
    'english': 'latin',
    'latin': 'latin',
    'en': 'latin',
    'tamil': 'ta',
    'ta': 'ta',
    'hindi': 'hi',
    'hi': 'hi',
    'devanagari': 'devanagari',
    'marathi': 'hi',
    'mr': 'hi',
    'telugu': 'te',
    'te': 'te',
    'kannada': 'kn',
    'kn': 'kn',
    'ka': 'ka',
    'malayalam': 'ml',
    'ml': 'ml',
}

MODEL_LANGUAGE_CODES = {
    'latin': 'latin',
    'ta': 'ta',
    'hi': 'devanagari',
    'devanagari': 'devanagari',
    'te': 'te',
    'kn': 'ka',
    'ka': 'ka',
    'ml': 'malayalam',
}

AUTO_LANGUAGES = ['latin', 'ta', 'hi', 'te', 'kn', 'ml']

LANG_MODEL_TARS = {
    'ta': 'ta_PP-OCRv4_rec_infer.tar',
    'latin': 'latin_PP-OCRv4_rec_infer.tar',
}


def _normalize_lang(lang):
    if not lang:
        raise ValueError("Language must be provided")
    key = lang.strip().lower()
    if key not in LANGUAGE_CODES:
        raise ValueError(
            f"Unsupported language '{lang}'. Supported languages: {', '.join(sorted(LANGUAGE_CODES.keys()))}"
        )
    return LANGUAGE_CODES[key]


def _get_model(lang):
    lang = _normalize_lang(lang)
    model_lang = MODEL_LANGUAGE_CODES.get(lang, lang)
    if model_lang not in ocr_models:
        ocr_models[model_lang] = _init_model(model_lang)
    return ocr_models[model_lang]


def _count_script_chars(texts, ranges):
    count = 0
    for text in texts:
        for ch in text:
            code = ord(ch)
            for start, end in ranges:
                if start <= code <= end:
                    count += 1
                    break
    return count


def _language_score(lang, texts, confidences):
    script_score = _count_script_chars(texts, SCRIPT_RANGES.get(lang, []))
    confidence_score = sum(confidences) if confidences else 0.0
    return script_score + 0.18 * len(texts) + 0.03 * confidence_score


def _select_best_language(results):
    best_lang = None
    best_score = -1.0
    for lang, data in results.items():
        texts, _, confidences = data
        score = _language_score(lang, texts, confidences)
        if score > best_score:
            best_score = score
            best_lang = lang
    return best_lang


def _select_header_language(results, image_height):
    if image_height <= 0:
        return None

    header_limit = image_height * 0.45
    best_header_detection = None
    ranked = []

    for lang, data in results.items():
        texts, boxes, confidences = data
        header_texts = []
        header_confidences = []

        for text, box, confidence in zip(texts, boxes, confidences):
            xmin, ymin, xmax, ymax = _rect_from_box(box)
            ycenter = (ymin + ymax) / 2.0
            if ycenter <= header_limit:
                header_texts.append(text)
                header_confidences.append(confidence)
                script_chars = _script_char_count(text, lang)
                area = max(0.0, xmax - xmin) * max(0.0, ymax - ymin)
                if lang != 'latin' and script_chars >= 2:
                    candidate = (area, script_chars, lang)
                    if best_header_detection is None or candidate > best_header_detection:
                        best_header_detection = candidate

        if not header_texts:
            continue

        ranked.append((lang, _language_score(lang, header_texts, header_confidences)))

    if best_header_detection and best_header_detection[0] >= 15000:
        return best_header_detection[2]

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[1], reverse=True)
    best_lang, best_score = ranked[0]
    next_score = ranked[1][1] if len(ranked) > 1 else 0.0

    if best_score >= 2.5 and best_score >= (next_score * 1.15):
        return best_lang

    return None


def _script_char_count(text, lang):
    return _count_script_chars([text], SCRIPT_RANGES.get(lang, []))


def _letterlike_chars(text):
    return [ch for ch in text if ch.isalpha()]


def _digit_chars(text):
    return [ch for ch in text if ch.isdigit()]


def _noise_chars(text):
    allowed = set(" -:.,/()₹")
    return [ch for ch in text if not (ch.isalnum() or ch.isspace() or ch in allowed)]


def _detection_score(lang, text, confidence):
    letters = _letterlike_chars(text)
    digits = _digit_chars(text)
    letter_count = len(letters)
    digit_count = len(digits)
    script_count = _script_char_count(text, lang)
    noise_count = len(_noise_chars(text))

    if letter_count == 0:
        ratio_bonus = 0.8 if digit_count else 0.0
    else:
        ratio_bonus = script_count / max(letter_count, 1)

    other_script_penalty = 0.0
    for script_lang in SCRIPT_RANGES:
        if script_lang == lang:
            continue
        other_script_penalty += _script_char_count(text, script_lang)

    return (
        (confidence * 4.0)
        + (ratio_bonus * 5.0)
        + min(len(text.strip()), 24) * 0.06
        + min(digit_count, 8) * 0.08
        - other_script_penalty * 0.18
        - noise_count * 0.35
    )


def _merge_auto_results(results):
    detections = []
    lang_counts = {}

    for lang, data in results.items():
        texts, boxes, confidences = data
        for text, box, confidence in zip(texts, boxes, confidences):
            text = text.strip()
            if not text:
                continue
            xmin, ymin, xmax, ymax = _rect_from_box(box)
            detections.append({
                'lang': lang,
                'text': text,
                'box': box,
                'confidence': float(confidence),
                'score': _detection_score(lang, text, float(confidence)),
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
                'ycenter': (ymin + ymax) / 2.0,
                'height': max(1.0, ymax - ymin),
            })

    if not detections:
        return [], [], [], {'mode': 'merged_auto', 'language_counts': {}, 'languages_tried': list(results.keys())}

    detections.sort(key=lambda item: item['ycenter'])
    avg_height = sum(item['height'] for item in detections) / len(detections)
    line_threshold = max(26.0, avg_height * 0.7)

    clusters = []
    current = [detections[0]]
    for item in detections[1:]:
        cluster_center = sum(entry['ycenter'] for entry in current) / len(current)
        if abs(item['ycenter'] - cluster_center) <= line_threshold:
            current.append(item)
        else:
            clusters.append(current)
            current = [item]
    clusters.append(current)

    merged = []
    for cluster in clusters:
        lang_groups = {}
        for item in cluster:
            lang_groups.setdefault(item['lang'], []).append(item)

        best_lang = None
        best_lang_score = float('-inf')
        for lang, items in lang_groups.items():
            group_score = sum(entry['score'] for entry in items)
            group_score += min(len(items), 6) * 0.25
            if group_score > best_lang_score:
                best_lang_score = group_score
                best_lang = lang

        selected = sorted(lang_groups[best_lang], key=lambda item: item['xmin'])
        for item in selected:
            lang_counts[item['lang']] = lang_counts.get(item['lang'], 0) + 1
        merged.extend(selected)

    merged.sort(key=lambda item: (item['ycenter'], item['xmin']))

    texts = [item['text'] for item in merged]
    boxes = [item['box'] for item in merged]
    confidences = [item['confidence'] for item in merged]
    metadata = {
        'mode': 'merged_auto',
        'language_counts': lang_counts,
        'languages_tried': list(results.keys()),
    }
    return texts, boxes, confidences, metadata


def _remove_cached_model(lang):
    cache_dir = Path.home() / ".paddleocr" / "whl" / "rec" / lang
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
        return True
    return False


def _init_model(lang):
    try:
        return PaddleOCR(lang=lang, use_angle_cls=False, use_space_char=True, show_log=False, enable_mkldnn=True)
    except (tarfile.ReadError, EOFError):
        if _remove_cached_model(lang):
            return PaddleOCR(lang=lang, use_angle_cls=False, use_space_char=True, show_log=False, enable_mkldnn=True)
        raise


def _load_models():
    _get_model('ta')
    _get_model('latin')

def _flatten_result(result):
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


def _image_variant_for_lang(image, lang):
    if isinstance(image, dict):
        if lang in image:
            return image[lang]
        return image.get('default')
    return image


def _rect_from_box(box):
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


def _box_iou(box1, box2):
    x1_min, y1_min, x1_max, y1_max = _rect_from_box(box1)
    x2_min, y2_min, x2_max, y2_max = _rect_from_box(box2)
    inter_xmin = max(x1_min, x2_min)
    inter_ymin = max(y1_min, y2_min)
    inter_xmax = min(x1_max, x2_max)
    inter_ymax = min(y1_max, y2_max)

    inter_w = max(0.0, inter_xmax - inter_xmin)
    inter_h = max(0.0, inter_ymax - inter_ymin)
    inter_area = inter_w * inter_h

    area1 = max(0.0, x1_max - x1_min) * max(0.0, y1_max - y1_min)
    area2 = max(0.0, x2_max - x2_min) * max(0.0, y2_max - y2_min)
    union_area = area1 + area2 - inter_area
    return inter_area / union_area if union_area else 0.0


def run_ocr(image, lang=None):
    """
    Extracts text, bounding boxes, and confidences from the preprocessed image.

    If lang is provided, this function uses the requested PaddleOCR language model.
    If lang is None, it tries all supported OCR languages and chooses the best result.
    """
    if lang is None:
        results = {}
        import numpy as np
        from paddleocr.tools.infer.utility import get_rotate_crop_image

        main_ocr = _get_model('latin')
        base_image = _image_variant_for_lang(image, 'default')
        det_res = main_ocr.ocr(base_image, cls=False, rec=False)
        boxes = det_res[0] if det_res and det_res[0] else []

        if not boxes:
            return [], [], [], {'mode': 'merged_auto', 'language_counts': {}, 'languages_tried': list(AUTO_LANGUAGES)}

        def process_candidate(candidate):
            try:
                candidate_image = _image_variant_for_lang(image, candidate)
                img_crops = []
                for box in boxes:
                    img_crop = get_rotate_crop_image(candidate_image, np.array(box, dtype=np.float32))
                    img_crops.append(img_crop)

                ocr = _get_model(candidate)
                rec_res = ocr.ocr(img_crops, det=False, cls=False)

                texts = []
                confidences = []
                if rec_res and rec_res[0]:
                    for item in rec_res[0]:
                        texts.append(item[0] if isinstance(item, (list, tuple)) else "")
                        confidences.append(float(item[1]) if isinstance(item, (list, tuple)) else 0.0)
                else:
                    texts = ["" for _ in boxes]
                    confidences = [0.0 for _ in boxes]
                    
                return candidate, (texts, list(boxes), confidences)
            except Exception:
                return candidate, None

        from concurrent.futures import as_completed
        with ThreadPoolExecutor(max_workers=min(len(AUTO_LANGUAGES), os.cpu_count() or 4)) as executor:
            future_to_lang = {executor.submit(process_candidate, candidate): candidate for candidate in AUTO_LANGUAGES}
            for future in as_completed(future_to_lang):
                candidate, res = future.result()
                if res:
                    results[candidate] = res

        if not results:
            raise RuntimeError("Unable to process image with any supported OCR model.")

        base_image = _image_variant_for_lang(image, 'default')
        header_lang = _select_header_language(results, base_image.shape[0] if hasattr(base_image, 'shape') else 0)
        if header_lang:
            texts, boxes, confidences = results[header_lang]
            return texts, boxes, confidences, {
                'mode': 'header_guided_single_language',
                'selected_language': header_lang,
                'languages_tried': list(results.keys()),
            }

        texts, boxes, confidences, metadata = _merge_auto_results(results)
        if texts:
            return texts, boxes, confidences, metadata

        best_lang = _select_best_language(results)
        texts, boxes, confidences = results[best_lang]
        return texts, boxes, confidences, {
            'mode': 'single_best_language',
            'selected_language': best_lang,
            'languages_tried': list(results.keys()),
        }

    ocr = _get_model(lang)
    selected_lang = _normalize_lang(lang)
    selected_image = _image_variant_for_lang(image, selected_lang)
    texts, boxes, confidences = _flatten_result(ocr.ocr(selected_image, cls=False))
    return texts, boxes, confidences, {
        'mode': 'single_language',
        'selected_language': selected_lang,
    }
