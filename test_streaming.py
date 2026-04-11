import requests, json, time

# Step 1: Upload files
print("--- Testing /api/upload ---")
files_to_upload = [
    ("files", ("sample_invoice (2).jpg", open("sample_data/sample_invoice (2).jpg", "rb"), "image/jpeg")),
    ("files", ("sample_english 1.jpg",   open("sample_data/sample_english 1.jpg",   "rb"), "image/jpeg")),
]
r = requests.post("http://localhost:8000/api/upload", files=files_to_upload)
print("Upload status:", r.status_code)
data = r.json()
print("Response:", data)
job_id = data["job_id"]
file_count = data["file_count"]

# Step 2: SSE stream
print()
print("--- Testing /api/stream/{job_id} ---")
start = time.time()
with requests.get(f"http://localhost:8000/api/stream/{job_id}", stream=True) as stream:
    for chunk in stream.iter_lines():
        if chunk:
            line = chunk.decode("utf-8")
            if line.startswith("data: "):
                result = json.loads(line[6:])
                if result.get("__done__"):
                    elapsed = round(time.time() - start, 1)
                    total = result["total"]
                    print(f"[DONE] All {total} images processed in {elapsed}s")
                else:
                    num    = result.get("image_number")
                    name   = result.get("image_name")
                    status = result.get("status")
                    text   = result.get("extracted_text", "")[:80].replace("\n", " ")
                    print(f"[{num}] {name} -> {status} | {text}")
