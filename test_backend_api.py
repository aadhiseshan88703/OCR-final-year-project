import requests
import time
import json
import sys

url = "http://localhost:8000/api/process"
file_path = "sample_data/sample_invoice (2).jpg"

print(f"Testing OCR API with file: {file_path}")
start_time = time.time()

try:
    with open(file_path, "rb") as f:
        files = {
            "files": ("sample_invoice (2).jpg", f, "image/jpeg")
        }
        res = requests.post(url, files=files)

    elapsed_time = time.time() - start_time
    print(f"Request completed in {elapsed_time:.2f} seconds.")
    
    if res.status_code == 200:
        print("Status Code 200: SUCCESS")
        data = res.json()
        print("Total Items Processed:", len(data.get("results", [])))
        result = data.get("results", [])[0]
        status = result.get("status")
        print("\n--- OCR Processing Result ---")
        print(f"Status: {status}")
        print("Language Tried in Backend (if captured):", status)
        if status == "success":
            print("\nExtracted Text Sample (first 200 chars):")
            print(result.get("extracted_text", "")[:200])
        else:
            print("Error Message:", result.get("error_message"))
            sys.exit(1)
    else:
        print(f"FAILED: Status {res.status_code}")
        print(res.text)
        sys.exit(1)
        
except Exception as e:
    print(f"Connection Exception: {e}")
    sys.exit(1)
