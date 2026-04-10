import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.pipeline import process_document
from src.postprocessing import save_json

app = FastAPI(title="OCR Invoice System API")

# Setup CORS to allow React frontend (default Vite port is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = os.path.join("sample_data", "temp_uploads")
OUTPUT_FILE = os.path.join("output", "result.json")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)

def reconstruct_text_from_layout(result):
    layout_data = result.get("layout", [])
    if layout_data:
        lines_dict = {}
        for item in layout_data:
            lid = item.get("line_id", 0)
            box = item.get("box", [[0,0]])
            xmin = min(p[0] for p in box)
            xmax = max(p[0] for p in box)
            if lid not in lines_dict:
                lines_dict[lid] = []
            lines_dict[lid].append({"text": item.get("text", ""), "xmin": xmin, "xmax": xmax})

        char_width = 12
        reconstructed_lines = []
        for lid in sorted(lines_dict.keys()):
            items = sorted(lines_dict[lid], key=lambda x: x["xmin"])
            line_str = ""
            last_xmax = 0
            
            for i, itm in enumerate(items):
                if i == 0:
                    line_str += itm["text"]
                else:
                    gap = itm["xmin"] - last_xmax
                    spaces = max(1, int(gap / char_width))
                    line_str += (" " * spaces) + itm["text"]
                last_xmax = itm["xmax"]
            
            reconstructed_lines.append(line_str)
        return "\n".join(reconstructed_lines)
    else:
        return "\n".join(result.get("text", []))

@app.post("/api/process")
async def process_files(files: List[UploadFile] = File(...)):
    """
    Accepts one or more image files, processes them sequentially,
    and returns the structured OCR results.
    """
    async def process_single_file(idx: int, file: UploadFile):
        file_path = os.path.join(TEMP_DIR, file.filename)
        
        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        entry = {
            "image_number": idx,
            "image_name": file.filename,
            "extracted_text": "",
            "structured_data": {},
            "status": "failed",
            "error_message": None
        }
        
        try:
            import asyncio
            # Process using existing OCR pipeline concurrently
            result = await asyncio.to_thread(process_document, file_path)
            
            extracted_text = reconstruct_text_from_layout(result)
            
            if not extracted_text.strip():
                entry["status"] = "failed"
                entry["error_message"] = "Image is not clear or no text could be extracted. Please upload a high-quality clearly visible image."
            else:
                structured_data = result.get("invoice_fields", {})
                
                entry["extracted_text"] = extracted_text
                entry["structured_data"] = structured_data
                entry["status"] = "success"
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            entry["status"] = "failed"
            entry["error_message"] = error_msg
            
        # Clean up temporary uploaded file
        try:
            os.remove(file_path)
        except OSError:
            pass
            
        return entry

    import asyncio
    tasks = [process_single_file(idx, file) for idx, file in enumerate(files, start=1)]
    output_data = await asyncio.gather(*tasks)

    # Save all results to output/result.json exactly like process_sequential.py
    save_json(output_data, OUTPUT_FILE)
    
    return JSONResponse(content={"results": output_data})

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "OCR backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
