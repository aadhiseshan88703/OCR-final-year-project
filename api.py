import os
import json
import uuid
import asyncio
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from src.pipeline import process_document
from src.postprocessing import save_json
from src.image_validator import validate_image_clarity


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load OCR models at startup to eliminate cold-start latency."""
    from src.ocr_engine import _load_models
    print("[startup] Pre-loading OCR models...")
    await asyncio.to_thread(_load_models)
    print("[startup] OCR models ready.")
    yield  # application runs here
    # (shutdown logic can go here if needed)


app = FastAPI(title="OCR Invoice System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_origin_regex=r"http://localhost(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control", "X-Accel-Buffering"],
)

TEMP_DIR = os.path.join("sample_data", "temp_uploads")
OUTPUT_FILE = os.path.join("output", "result.json")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

# ── In-memory job store: job_id → list of {path, original_name, idx} ─────────
_job_store: dict = {}


# Model pre-loading is handled by the lifespan context manager above.


# ── Shared text reconstruction helper ─────────────────────────────────────────
def reconstruct_text_from_layout(result):
    layout_data = result.get("layout", [])
    if layout_data:
        lines_dict = {}
        for item in layout_data:
            lid = item.get("line_id", 0)
            box = item.get("box", [[0, 0]])
            xmin = min(p[0] for p in box)
            xmax = max(p[0] for p in box)
            lines_dict.setdefault(lid, []).append(
                {"text": item.get("text", ""), "xmin": xmin, "xmax": xmax}
            )
        char_width = 12
        lines = []
        for lid in sorted(lines_dict.keys()):
            items = sorted(lines_dict[lid], key=lambda x: x["xmin"])
            line_str = ""
            last_xmax = 0
            for i, itm in enumerate(items):
                if i == 0:
                    line_str += itm["text"]
                else:
                    spaces = max(1, int((itm["xmin"] - last_xmax) / char_width))
                    line_str += (" " * spaces) + itm["text"]
                last_xmax = itm["xmax"]
            lines.append(line_str)
        return "\n".join(lines)
    return "\n".join(result.get("text", []))


# ── Shared per-file OCR logic ──────────────────────────────────────────────────
async def _process_one(idx: int, file_path: str, original_name: str) -> dict:
    entry = {
        "image_number": idx,
        "image_name": original_name,
        "extracted_text": "",
        "structured_data": {},
        "status": "failed",
        "error": None,
        "error_message": None,
    }
    try:
        # Step 0: Clarity validation
        is_clear, clarity_reason = await asyncio.to_thread(
            validate_image_clarity, file_path
        )
        if not is_clear:
            entry["error"] = "Image quality check failed"
            entry["error_message"] = clarity_reason
            return entry

        # Steps 1-3: OCR pipeline
        result = await asyncio.to_thread(process_document, file_path)
        extracted_text = reconstruct_text_from_layout(result)

        if not extracted_text.strip():
            entry["error"] = "No text extracted"
            entry["error_message"] = (
                "No text could be extracted. "
                "Please upload a high-quality, clearly visible image."
            )
        else:
            entry["extracted_text"] = extracted_text
            entry["structured_data"] = result.get("invoice_fields", {})
            entry["status"] = "success"
            entry["error"] = None
            entry["error_message"] = None

    except Exception as e:
        entry["error"] = f"{type(e).__name__}"
        entry["error_message"] = str(e)
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass

    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1 — Two-step streaming  (used by the React frontend for live results)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/upload")
async def upload_for_streaming(files: List[UploadFile] = File(...)):
    """
    Step 1 of 2 for streaming mode.
    Saves uploaded files to temp storage and returns a job_id.
    The client then connects to GET /api/stream/{job_id} for live results.
    """
    job_id = str(uuid.uuid4())
    file_infos = []

    for idx, file in enumerate(files, start=1):
        safe_name = f"{job_id}_{idx:04d}_{file.filename}"
        file_path = os.path.join(TEMP_DIR, safe_name)
        content = await file.read()
        with open(file_path, "wb") as buf:
            buf.write(content)
        file_infos.append(
            {"path": file_path, "original_name": file.filename, "idx": idx}
        )

    _job_store[job_id] = file_infos
    return {"job_id": job_id, "file_count": len(file_infos)}


@app.get("/api/stream/{job_id}")
async def stream_results(job_id: str):
    """
    Step 2 of 2 for streaming mode.
    Server-Sent Events (SSE) endpoint — processes images one-by-one in upload
    order and pushes each result to the client as it finishes.
    """
    if job_id not in _job_store:
        return JSONResponse({"error": "Job not found or already consumed."}, status_code=404)

    file_infos = _job_store.pop(job_id)

    async def event_generator():
        all_results = []
        try:
            for info in file_infos:
                result = await _process_one(info["idx"], info["path"], info["original_name"])
                all_results.append(result)
                # Push result to client immediately
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

            # Save consolidated JSON after all images processed
            save_json(all_results, OUTPUT_FILE)

            # Signal stream completion
            done_event = {"__done__": True, "total": len(all_results)}
            yield f"data: {json.dumps(done_event)}\n\n"

        except asyncio.CancelledError:
            # Client disconnected mid-stream — save whatever we have and exit cleanly.
            # Do NOT re-raise: that would crash the uvicorn worker process.
            if all_results:
                save_json(all_results, OUTPUT_FILE)
            # Clean up any temp files that were never processed
            processed_paths = {r.get("image_name") for r in all_results}
            for info in file_infos:
                if info["original_name"] not in processed_paths:
                    try:
                        os.remove(info["path"])
                    except OSError:
                        pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2 — Legacy single-call (kept for backward-compat / CLI tests)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/process")
async def process_files(files: List[UploadFile] = File(...)):
    """
    Accepts one or more uploaded image files.
    Processes them sequentially in upload order and returns all results at once.
    (Use /api/upload + /api/stream/{job_id} for real-time streaming.)
    """
    output_data = []

    for idx, file in enumerate(files, start=1):
        safe_name = f"{idx:04d}_{file.filename}"
        file_path = os.path.join(TEMP_DIR, safe_name)

        content = await file.read()
        with open(file_path, "wb") as buf:
            buf.write(content)

        result = await _process_one(idx, file_path, file.filename)
        output_data.append(result)

    save_json(output_data, OUTPUT_FILE)
    return JSONResponse(content={"results": output_data})


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "OCR backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
