import json
import os
import re
import time

DEVANAGARI_DIGITS = str.maketrans('??????????', '0123456789')
TAMIL_DIGITS = str.maketrans('??????????', '0123456789')
TELUGU_DIGITS = str.maketrans('??????????', '0123456789')
BENGALI_DIGITS = str.maketrans('??????????', '0123456789')
GUJARATI_DIGITS = str.maketrans('??????????', '0123456789')
KANNADA_DIGITS = str.maketrans('??????????', '0123456789')
MALAYALAM_DIGITS = str.maketrans('??????????', '0123456789')
ALL_DIGITS = {
    **DEVANAGARI_DIGITS,
    **TAMIL_DIGITS,
    **TELUGU_DIGITS,
    **BENGALI_DIGITS,
    **GUJARATI_DIGITS,
    **KANNADA_DIGITS,
    **MALAYALAM_DIGITS,
}

SCRIPT_KEEP_RANGES = {
    'te': [(0x0C00, 0x0C7F)],
    'ta': [(0x0B80, 0x0BFF)],
    'hi': [(0x0900, 0x097F)],
    'devanagari': [(0x0900, 0x097F)],
    'bn': [(0x0980, 0x09FF)],
    'gu': [(0x0A80, 0x0AFF)],
    'kn': [(0x0C80, 0x0CFF)],
    'ml': [(0x0D00, 0x0D7F)],
}

TAMIL_TOTAL_KEYWORDS = [
    '?????', '???????', '????', '???', '???????', '??.???.??',
    'total', 'subtotal', 'amount', 'grand total', '?'
]
TAMIL_INVOICE_KEYWORDS = ['invoice', 'bill', '????', '????', '??????']
TAMIL_PHONE_KEYWORDS = ['phone', '???', '????????', '????']

TELUGU_TOTAL_KEYWORDS = ['??????', '???????', '?????? ???????????????', '?????', '?????? ??', '??']
TELUGU_INVOICE_KEYWORDS = ['????', '?????????', '???? ??', '???? ?????', '?????']
TELUGU_PHONE_KEYWORDS = ['????', '??????', '????????????', '??????????']
TELUGU_DATE_KEYWORDS = ['????', '?????', '????????', '??????', '???????', '??', '????', '????', '??????', '??????????', '????????', '??????', '????????']

LANGUAGE_LABELS = {
    'ta': 'Tamil',
    'te': 'Telugu',
    'hi': 'Hindi/Marathi (Devanagari)',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
}

SUPPORTED_OCR_LANGS = {'ta', 'te', 'hi', 'kn'}
TARGET_LANGS = {'ta', 'te', 'hi', 'bn', 'gu', 'kn', 'ml'}


def _normalize_number(text):
    # Convert Indic digits to Latin digits
    n = text.translate(ALL_DIGITS)
    n = n.replace('?', '').replace('Rs', '').replace('??', '').replace('??', '').strip()
    n = n.replace(',', '')
    return n


def _to_float(value):
    try:
        return float(value)
    except ValueError:
        cleaned = re.sub(r'[^0-9.\-]', '', value)
        try:
            return float(cleaned)
        except ValueError:
            return None


def _extract_invoice_fields(texts, boxes):
    fields = {
        'invoice_no': None,
        'date': None,
        'phone': None,
        'sub_total': None,
        'tax': None,
        'grand_total': None
    }

    number_pattern = re.compile(r'[0-9?-??-?]+(?:[.,][0-9?-??-?]+)?')
    candidates = []

    # Determine y position of each text block for bottom-of-page heuristics
    y_centers = []
    for box in boxes:
        if box and len(box) == 4:
            y_coords = [p[1] for p in box]
            y_centers.append(sum(y_coords) / len(y_coords))
        else:
            y_centers.append(0)

    max_y = max(y_centers) if y_centers else 0

    for idx, t in enumerate(texts):
        t_stripped = t.strip()
        t_lower = t_stripped.lower()

        # Date patterns
        if fields['date'] is None:
            dmatch = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', t_stripped)
            if dmatch:
                fields['date'] = dmatch.group(1)
            elif any(key in t_stripped for key in TELUGU_DATE_KEYWORDS):
                fields['date'] = t_stripped

        # Invoice number
        if fields['invoice_no'] is None and any(key in t_lower for key in ['invoice', 'bill', '???? ??????', '??.', '??'] + TAMIL_INVOICE_KEYWORDS + TELUGU_INVOICE_KEYWORDS):
            m = number_pattern.search(t_stripped)
            if m:
                fields['invoice_no'] = _normalize_number(m.group(0))

        # Phone number
        if fields['phone'] is None and any(key in t_lower for key in ['phone', '???'] + TAMIL_PHONE_KEYWORDS + TELUGU_PHONE_KEYWORDS):
            m = number_pattern.search(t_stripped)
            if m and len(re.sub(r'[^0-9]', '', _normalize_number(m.group(0)))) >= 6:
                fields['phone'] = _normalize_number(m.group(0))

        # Numeric candidates for totals
        for m in number_pattern.findall(t_stripped):
            n = _to_float(_normalize_number(m))
            if n is not None:
                candidates.append({
                    'value': n,
                    'text': t_stripped,
                    'y': y_centers[idx] if idx < len(y_centers) else 0,
                    'is_total_label': any(key in t_lower for key in ['??? ???', '??? ????', 'total', 'grand total', 'amount', '?', '?? ?? ??', 'tax'] + TAMIL_TOTAL_KEYWORDS + TELUGU_TOTAL_KEYWORDS)
                })

    # Parse labeled totals first
    for c in candidates:
        ln = c['text'].lower()
        val = c['value']
        if 'tax' in ln or 'gst' in ln or '?? ?? ??' in ln:
            fields['tax'] = val
        elif 'grand' in ln or '???' in ln or '??????' in ln or '??? ???' in ln or ('total' in ln and 'sub' not in ln):
            fields['grand_total'] = val
        elif 'sub' in ln or '???????' in ln or '?????' in ln or '??????' in ln or 'total' in ln:
            if fields['sub_total'] is None:
                fields['sub_total'] = val

        if fields['phone'] is None:
            normalized_digits = re.sub(r'[^0-9]', '', _normalize_number(c['text']))
            if len(normalized_digits) == 10:
                fields['phone'] = normalized_digits

    # Fallback from bottom-of-page numeric candidates (common total area)
    if fields['grand_total'] is None and candidates:
        bottom_candidates = [c for c in candidates if c['y'] >= max_y * 0.75 and c['value'] < 100000]
        if bottom_candidates:
            fields['grand_total'] = max(c['value'] for c in bottom_candidates)

    # Fallback from decimal/large numbers excluding phone-like values
    if fields['grand_total'] is None:
        decimal_candidates = [c['value'] for c in candidates if c['value'] < 100000 and (not float(c['value']).is_integer() or 100 < c['value'] < 10000)]
        if decimal_candidates:
            fields['grand_total'] = max(decimal_candidates)

    # Fallback to reasonable maximum if still missing
    if fields['grand_total'] is None:
        reasonable = [c['value'] for c in candidates if c['value'] < 100000]
        if reasonable:
            fields['grand_total'] = max(reasonable)

    return fields


def _char_allowed_for_lang(ch, lang):
    if ch.isdigit() or ch.isspace() or ch in ".,:/-()?":
        return True
    for start, end in SCRIPT_KEEP_RANGES.get(lang, []):
        if start <= ord(ch) <= end:
            return True
    return False


def _cleanup_script_specific_entries(texts, boxes, confidences, lang):
    if lang not in SCRIPT_KEEP_RANGES:
        return texts, boxes, confidences

    cleaned_texts = []
    cleaned_boxes = []
    cleaned_confidences = []
    for text, box, confidence in zip(texts, boxes, confidences):
        compact = ''.join(ch for ch in text if _char_allowed_for_lang(ch, lang)).strip()
        script_chars = sum(
            1 for ch in compact
            if any(start <= ord(ch) <= end for start, end in SCRIPT_KEEP_RANGES[lang])
        )
        digit_chars = sum(1 for ch in compact if ch.isdigit())
        if script_chars >= 1 or digit_chars >= 3:
            cleaned_texts.append(compact)
            cleaned_boxes.append(box)
            cleaned_confidences.append(confidence)
    return cleaned_texts, cleaned_boxes, cleaned_confidences


def _detect_language_for_text(text):
    counts = {}
    for lang in TARGET_LANGS:
        ranges = SCRIPT_KEEP_RANGES.get(lang, [])
        if not ranges:
            continue
        count = 0
        for ch in text:
            code = ord(ch)
            for start, end in ranges:
                if start <= code <= end:
                    count += 1
                    break
        counts[lang] = count

    best_lang = None
    best_count = 0
    for lang, count in counts.items():
        if count > best_count:
            best_count = count
            best_lang = lang

    return best_lang if best_count >= 1 else None


def _group_by_language(texts, boxes, confidences):
    grouped = {label: [] for label in LANGUAGE_LABELS.values()}
    layout = []
    line_layout = []

    items = []
    for text, box, confidence in zip(texts, boxes, confidences):
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)
        items.append({
            'text': text,
            'box': box,
            'confidence': float(confidence),
            'xmin': xmin,
            'xmax': xmax,
            'ymin': ymin,
            'ymax': ymax,
            'ycenter': (ymin + ymax) / 2.0,
            'height': max(1.0, ymax - ymin),
        })

    if items:
        avg_height = sum(item['height'] for item in items) / len(items)
    else:
        avg_height = 30.0
    line_threshold = max(26.0, avg_height * 0.7)

    items.sort(key=lambda item: item['ycenter'])
    clusters = []
    current = []
    for item in items:
        if not current:
            current = [item]
            continue
        center = sum(entry['ycenter'] for entry in current) / len(current)
        if abs(item['ycenter'] - center) <= line_threshold:
            current.append(item)
        else:
            clusters.append(current)
            current = [item]
    if current:
        clusters.append(current)

    line_id = 0
    for cluster in clusters:
        cluster.sort(key=lambda item: item['xmin'])
        line_text = ' '.join(item['text'] for item in cluster).strip()
        lang = _detect_language_for_text(line_text)
        label = LANGUAGE_LABELS.get(lang)
        avg_conf = sum(item['confidence'] for item in cluster) / len(cluster)
        entry = {
            'line_id': line_id,
            'text': line_text,
            'boxes': [item['box'] for item in cluster],
            'confidence': round(avg_conf, 4),
        }
        if label:
            grouped[label].append(entry)
        line_layout.append({
            'line_id': line_id,
            'text': line_text,
            'language': label or 'Unknown',
            'boxes': [item['box'] for item in cluster],
            'confidence': round(avg_conf, 4),
        })
        for item in cluster:
            layout.append({
                'line_id': line_id,
                'text': item['text'],
                'box': item['box'],
                'confidence': item['confidence'],
                'language': label or 'Unknown',
            })
        line_id += 1

    summary = []
    for lang, label in LANGUAGE_LABELS.items():
        items = grouped[label]
        if items:
            char_count = sum(len(item['text']) for item in items)
            avg_conf = sum(item['confidence'] for item in items) / len(items)
            summary.append({
                'language': label,
                'char_count': char_count,
                'avg_confidence': round(avg_conf, 4),
            })

    return grouped, summary, layout, line_layout


def postprocess(texts, boxes, confidences, ocr_metadata=None):
    """
    Cleans extracted text and formats the output into structured JSON.
    """
    entries = [(t.strip(), b, c) for t, b, c in zip(texts, boxes, confidences) if t.strip()]
    cleaned_texts = [t for t, _, _ in entries]
    cleaned_boxes = [b for _, b, _ in entries]
    cleaned_confidences = [c for _, _, c in entries]
    selected_lang = (ocr_metadata or {}).get("selected_language")
    # Disabled script cleanup to preserve exact text as it appears in the image, mixed languages included

    invoice_fields = _extract_invoice_fields(cleaned_texts, cleaned_boxes)
    grouped, summary, layout, line_layout = _group_by_language(cleaned_texts, cleaned_boxes, cleaned_confidences)
    formatted_data = {
        "text": cleaned_texts,
        "boxes": cleaned_boxes,
        "confidence": cleaned_confidences,
        "ocr_metadata": ocr_metadata or {},
        "language_summary": {
            "detected": summary,
            "unsupported_models": sorted(TARGET_LANGS - SUPPORTED_OCR_LANGS),
            "notes": [
                "Hindi and Marathi share the Devanagari script; they are grouped together.",
                "Bengali, Gujarati, and Malayalam detection is based on script ranges; OCR model support may be limited.",
            ],
        },
        "language_sections": grouped,
        "layout": layout,
        "line_layout": line_layout,
        "invoice_fields": invoice_fields
    }
    return formatted_data


def save_json(data, path="output/result.json"):
    """
    Saves the structured data to a JSON file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        try:
            os.replace(temp_path, path)
            return path
        except PermissionError:
            fallback_path = path.replace('.json', f'.{int(time.time())}.json')
            os.replace(temp_path, fallback_path)
            return fallback_path
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
