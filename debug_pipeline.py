import sys, time, traceback
sys.stdout.reconfigure(encoding='utf-8')

# ── Pre-load models (same as lifespan does) ────────────────────────────────
print("[1/4] Loading OCR models...")
t0 = time.time()
from src.ocr_engine import _load_models
_load_models()
print(f"      Models loaded in {time.time()-t0:.1f}s")

# ── Run single-image pipeline ──────────────────────────────────────────────
from src.pipeline import process_document
from src.image_validator import validate_image_clarity

TEST_IMAGE = r"sample_data\sample_invoice (2).jpg"

print(f"\n[2/4] Validating image: {TEST_IMAGE}")
try:
    ok, reason = validate_image_clarity(TEST_IMAGE)
    if ok:
        print("      Image OK")
    else:
        print(f"      VALIDATION FAILED: {reason}")
        sys.exit(1)
except Exception:
    traceback.print_exc()
    sys.exit(1)

print("\n[3/4] Running OCR pipeline...")
t1 = time.time()
try:
    result = process_document(TEST_IMAGE)
    elapsed = time.time() - t1
    print(f"      Pipeline finished in {elapsed:.1f}s")
    text = "\n".join(result.get("text", []))
    print(f"      Extracted text ({len(text)} chars): {text[:200]!r}")
    fields = result.get("invoice_fields", {})
    print(f"      Invoice fields: {fields}")
except Exception:
    print("\n===== PIPELINE CRASH =====")
    traceback.print_exc()
    sys.exit(1)

print("\n[4/4] All tests PASSED ✓")
