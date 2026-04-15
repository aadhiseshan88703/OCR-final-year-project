import os
import sys
import json
import traceback

from src.pipeline import process_document
from src.postprocessing import save_json
from src.image_validator import validate_image_clarity

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

def process_images_sequentially(input_dir="sample_data", output_file=os.path.join("output", "result.json")):
    """
    Reads images from input_dir, processes them ONE BY ONE sequentially,
    and writes results to output_file preserving the exact input order.
    """
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        sys.exit(1)
        
    images = []
    for f in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, f)) and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
            images.append(f)
            
    images.sort() # Strict lexicographical order to ensure determinism
    
    output_data = []
    print(f"Found {len(images)} images in '{input_dir}'.")
    
    for idx, img_name in enumerate(images, start=1):
        img_path = os.path.join(input_dir, img_name)
        print(f"\n[{idx}/{len(images)}] Processing: {img_name}")
        
        entry = {
            "image_number": idx,
            "image_name": img_name,
            "extracted_text": "",
            "structured_data": {},
            "status": "failed",
            "error_message": None
        }
        
        is_clear, clarity_reason = validate_image_clarity(img_path)
        if not is_clear:
            print(f" -> Skipped (image not clear): {clarity_reason}")
            entry["status"] = "failed"
            entry["error"] = "Image is not clear enough for extraction"
            entry["error_message"] = clarity_reason
            output_data.append(entry)
            save_json(output_data, output_file)
            print(f" -> Intermediate results saved to {output_file}.")
            continue

        try:
            result = process_document(img_path)
            
            layout_data = result.get("layout", [])
            if layout_data:
                # Group by line_id
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
                            # Try to keep some left indent if we want, or just start
                            line_str += itm["text"]
                        else:
                            gap = itm["xmin"] - last_xmax
                            spaces = max(1, int(gap / char_width))
                            line_str += (" " * spaces) + itm["text"]
                        last_xmax = itm["xmax"]
                    
                    reconstructed_lines.append(line_str)
                extracted_text = "\n".join(reconstructed_lines)
            else:
                extracted_text = "\n".join(result.get("text", []))
                
            structured_data = result.get("invoice_fields", {})
            
            entry["extracted_text"] = extracted_text
            entry["structured_data"] = structured_data
            entry["status"] = "success"
            print(f" -> Success! Found {len(result.get('text', []))} lines of text.")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f" -> Failed to process {img_name}: {error_msg}")
            entry["status"] = "failed"
            entry["error_message"] = error_msg
            
        output_data.append(entry)
        
        save_json(output_data, output_file)
        print(f" -> Intermediate results saved to {output_file}.")
        
    print(f"\nSequential processing complete. Total 100% finished. Results in {output_file}")

if __name__ == "__main__":
    input_directory = sys.argv[1] if len(sys.argv) > 1 else "sample_data"
    out_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join("output", "result.json")
    process_images_sequentially(input_dir=input_directory, output_file=out_file)
