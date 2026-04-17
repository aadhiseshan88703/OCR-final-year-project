import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import logging
import shutil
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from paddleocr import PaddleOCR
from paddleocr.tools.infer.utility import get_rotate_crop_image

from src.preprocessing import _telugu_enhanced_variant

logging.getLogger("ppocr").setLevel(logging.ERROR)

ocr_models = {}

SUPPORTED_LANGUAGES = {
    'latin': 'Latin/English',
    'ta': 'Tamil',
    'hi': 'Hindi/Devanagari',
    'devanagari': 'Hindi/Devanagari',
    'mr': 'Marathi',          # uses Devanagari model
    'te': 'Telugu',
    'kn': 'Kannada',
    'ka': 'Kannada',
    'guj': 'Gujarati',
    'ben': 'Bengali',
}

SCRIPT_RANGES = {
    'latin': [(0x0041, 0x005A), (0x0061, 0x007A)],
    'ta':    [(0x0B80, 0x0BFF)],
    'hi':    [(0x0900, 0x097F)],
    'devanagari': [(0x0900, 0x097F)],
    'mr':    [(0x0900, 0x097F)],   # Marathi
    'kn':    [(0x0C80, 0x0CFF)],
    'ka':    [(0x0C80, 0x0CFF)],
    'te':    [(0x0C00, 0x0C7F)],
    'ml':    [(0x0D00, 0x0D7F)],
    'ben':   [(0x0980, 0x09FF)],   # Bengali
    'guj':   [(0x0A80, 0x0AFF)],   # Gujarati
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
    'marathi': 'mr',
    'mr': 'mr',
    'telugu': 'te',
    'te': 'te',
    'kannada': 'kn',
    'kn': 'kn',
    'ka': 'ka',
    'gujarati': 'guj',
    'guj': 'guj',
    'gu': 'guj',
    'bengali': 'ben',
    'ben': 'ben',
    'bn': 'ben',
}

# Maps internal lang key → PaddleOCR model lang code.
# NOTE: 'gu' (Gujarati) and 'bn' (Bengali) are NOT available in PP-OCRv4.
# PaddleOCR will automatically fall back to the best available older model
# (PP-OCRv3) for these two languages.  Accuracy is slightly lower but
# functional.  All other languages use PP-OCRv4 models.
MODEL_LANGUAGE_CODES = {
    'latin': 'latin',
    'ta': 'ta',
    'hi': 'devanagari',
    'devanagari': 'devanagari',
    'mr': 'devanagari',
    'te': 'te',
    'kn': 'ka',
    'ka': 'ka',
    'guj': 'gu',   # PP-OCRv3 fallback — Gujarati not in PP-OCRv4
    'ben': 'bn',   # PP-OCRv3 fallback — Bengali not in PP-OCRv4
}

# Languages tried automatically when no lang is specified.
AUTO_LANGUAGES = ['latin', 'ta', 'hi', 'te', 'kn', 'guj', 'ben', 'mr']


def _is_gpu_available():
    try:
        import paddle
        return paddle.is_compiled_with_cuda()
    except Exception:
        return False

USE_GPU = _is_gpu_available()


def _variant_key(lang):
    return 'te' if lang == 'te' else 'default'


def _prepare_image_crops(image_variant, boxes):
    if not boxes:
        return []
    return [get_rotate_crop_image(image_variant, np.array(box, dtype=np.float32)) for box in boxes]


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
    ranges = SCRIPT_RANGES.get(lang, [])
    script_chars = _count_script_chars(texts, ranges)
    total_chars = sum(len(text) for text in texts)
    letter_chars = sum(sum(1 for ch in text if ch.isalpha()) for text in texts)
    other_script_chars = 0
    for other_lang, other_ranges in SCRIPT_RANGES.items():
        if other_lang == lang:
            continue
        other_script_chars += _count_script_chars(texts, other_ranges)

    script_ratio = script_chars / max(letter_chars, 1)
    confidence_score = sum(confidences) if confidences else 0.0
    noise_chars = max(0, total_chars - script_chars)

    return (
        script_chars * 4.5
        + script_ratio * 20.0
        + 0.035 * confidence_score
        - other_script_chars * 3.0
        - noise_chars * 0.15
        + 0.08 * len(texts)
    )


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


def _remove_cached_model(lang):
    cache_dir = Path.home() / ".paddleocr" / "whl" / "rec" / lang
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
        return True
    return False


def _init_model(lang):
    try:
        return PaddleOCR(
            lang=lang,
            use_angle_cls=False,
            use_space_char=True,
            show_log=False,
            enable_mkldnn=True,
            use_gpu=USE_GPU,
        )
    except (tarfile.ReadError, EOFError):
        if _remove_cached_model(lang):
            return PaddleOCR(
                lang=lang,
                use_angle_cls=False,
                use_space_char=True,
                show_log=False,
                enable_mkldnn=True,
                use_gpu=USE_GPU,
            )
        raise


def _load_models():
    """
    Pre-load ALL supported OCR language models into the model cache.
    Called once at server startup so the first user request has no cold-start delay.
    Failures for individual languages are logged as warnings (non-fatal).
    NOTE: Gujarati ('gu') and Bengali ('bn') use PP-OCRv3 models — still functional
    but with slightly lower accuracy than PP-OCRv4 languages.
    """
    for lang in AUTO_LANGUAGES:
        try:
            _get_model(lang)
            logging.info(f"Model pre-loaded: {lang}")
        except Exception as exc:
            logging.warning(f"Could not pre-load model for '{lang}': {exc}")


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
        if lang == 'te':
            image['te'] = _telugu_enhanced_variant(image['default'])
            return image['te']
        return image.get('default')
    return image


def _rect_from_box(box):
    x_coords = [point[0] for point in box]
    y_coords = [point[1] for point in box]
    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


def run_ocr(image, lang=None):
    """
    Extracts text, bounding boxes, and confidences from the preprocessed image.

    If lang is provided, this function uses the requested PaddleOCR language model.
    If lang is None, it tries all supported OCR languages and returns only the
    single detected language output for the image.
    """
    if lang is None:
        main_ocr = _get_model('latin')
        base_image = _image_variant_for_lang(image, 'default')
        det_res = main_ocr.ocr(base_image, cls=False, rec=False)
        boxes = det_res[0] if det_res and det_res[0] else []

        if not boxes:
            return [], [], [], {'mode': 'merged_auto', 'language_counts': {}, 'languages_tried': list(AUTO_LANGUAGES)}

        attempted_languages = []
        failed_languages = []
        results = {}

        # Pre-compute image crops per variant (default vs telugu-enhanced)
        crops_by_variant = {}
        for candidate in AUTO_LANGUAGES:
            variant_name = _variant_key(candidate)
            if variant_name not in crops_by_variant:
                variant_image = _image_variant_for_lang(image, candidate)
                crops_by_variant[variant_name] = _prepare_image_crops(variant_image, boxes)

        def process_candidate(candidate):
            try:
                crop_key = _variant_key(candidate)
                img_crops = crops_by_variant[crop_key]
                if not img_crops:
                    return candidate, None, True  # (lang, result, failed)

                ocr = _get_model(candidate)
                rec_res = ocr.ocr(img_crops, det=False, cls=False)

                texts = []
                confidences = []
                if rec_res and rec_res[0]:
                    for item in rec_res[0]:
                        texts.append(item[0] if isinstance(item, (list, tuple)) else "")
                        confidences.append(float(item[1]) if isinstance(item, (list, tuple)) else 0.0)
                else:
                    texts = ["" for _ in img_crops]
                    confidences = [0.0 for _ in img_crops]

                return candidate, (texts, list(boxes), confidences), False
            except Exception:
                return candidate, None, True

        max_workers = min(len(AUTO_LANGUAGES), max(1, (os.cpu_count() or 4) // 2))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_lang = {
                executor.submit(process_candidate, candidate): candidate
                for candidate in AUTO_LANGUAGES
            }
            for future in as_completed(future_to_lang):
                candidate, res, failed = future.result()
                attempted_languages.append(candidate)
                if failed:
                    failed_languages.append(candidate)
                elif res:
                    results[candidate] = res

        if not results:
            raise RuntimeError("Unable to process image with any supported OCR model.")

        language_scores = {
            lang_key: round(_language_score(lang_key, texts, confidences), 4)
            for lang_key, (texts, _, confidences) in results.items()
        }
        best_lang = _select_best_language(results)
        texts, boxes, confidences = results[best_lang]
        return texts, boxes, confidences, {
            'mode': 'single_best_language',
            'selected_language': best_lang,
            'languages_tried': attempted_languages,
            'languages_failed': failed_languages,
            'language_scores': language_scores,
        }

    ocr = _get_model(lang)
    selected_lang = _normalize_lang(lang)
    selected_image = _image_variant_for_lang(image, selected_lang)
    texts, boxes, confidences = _flatten_result(ocr.ocr(selected_image, cls=False))
    return texts, boxes, confidences, {
        'mode': 'single_language',
        'selected_language': selected_lang,
    }
