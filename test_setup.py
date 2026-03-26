"""
Test Script - OCR Invoice System Setup Verification
This script verifies all modules and creates test data.
Run this after installing dependencies with: python test_setup.py
"""

import os
import sys

def check_imports():
    """Check if all required packages are installed"""
    print("=" * 60)
    print("🔍 CHECKING IMPORTED MODULES")
    print("=" * 60)
    
    required_packages = {
        'cv2': 'opencv-python',
        'paddleocr': 'paddleocr',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'paddle': 'paddlepaddle'
    }
    
    missing_packages = []
    
    for package_name, pip_name in required_packages.items():
        try:
            __import__(package_name)
            print(f"✅ {pip_name:20} - INSTALLED")
        except ImportError:
            print(f"❌ {pip_name:20} - MISSING")
            missing_packages.append(pip_name)
    
    print("=" * 60)
    
    if missing_packages:
        print("\n⚠️  MISSING PACKAGES:")
        print(f"Run this command to install them:")
        print(f"\npython -m pip install {' '.join(missing_packages)}\n")
        return False
    else:
        print("✅ All required packages are installed!\n")
        return True

def check_file_structure():
    """Verify project folder structure"""
    print("=" * 60)
    print("📁 CHECKING PROJECT STRUCTURE")
    print("=" * 60)
    
    required_files = {
        'main.py': 'Entry point',
        'requirements.txt': 'Dependencies list',
        'src/__init__.py': 'Package init',
        'src/preprocessing.py': 'Image preprocessing',
        'src/ocr_engine.py': 'OCR engine',
        'src/postprocessing.py': 'Output formatting',
        'src/pipeline.py': 'Pipeline orchestration',
        'sample_data': 'Sample data folder',
        'output': 'Output folder',
    }
    
    missing_files = []
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path:30} - {description}")
        else:
            print(f"❌ {file_path:30} - {description} (MISSING)")
            missing_files.append(file_path)
    
    print("=" * 60)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files/folders\n")
        return False
    else:
        print("✅ All required files are present!\n")
        return True

def create_sample_image():
    """Create a sample invoice image for testing"""
    print("=" * 60)
    print("🖼️  CREATING SAMPLE INVOICE IMAGE")
    print("=" * 60)
    
    try:
        import cv2
        import numpy as np
        
        # Create white canvas
        img = np.ones((600, 800, 3), dtype=np.uint8) * 255
        
        # Add header
        cv2.rectangle(img, (30, 30), (770, 100), (200, 200, 200), -1)
        cv2.putText(img, 'INVOICE', (300, 75), cv2.FONT_HERSHEY_BOLD, 2.5, (0, 0, 0), 3)
        
        # Add store name
        cv2.putText(img, 'ABC Store', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        cv2.putText(img, 'Phone: +91 98765 43210', (50, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 1)
        
        # Add bill lines
        y_pos = 250
        cv2.putText(img, 'Item                    Qty    Price', (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        cv2.line(img, (50, y_pos + 15), (750, y_pos + 15), (0, 0, 0), 1)
        
        y_pos = 310
        cv2.putText(img, 'Product A               2      100', (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        y_pos = 360
        cv2.putText(img, 'Product B               1      200', (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        y_pos = 410
        cv2.putText(img, 'Discount                        -50', (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        # Total amount
        y_pos = 470
        cv2.line(img, (50, y_pos), (750, y_pos), (0, 0, 0), 2)
        cv2.putText(img, 'TOTAL AMOUNT: 350', (50, y_pos + 50), cv2.FONT_HERSHEY_BOLD, 1.2, (0, 0, 200), 2)
        
        # Date
        cv2.putText(img, 'Date: 25/03/2026', (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
        
        # Save image
        cv2.imwrite('sample_data/sample_invoice.jpg', img)
        print("✅ Sample invoice created at: sample_data/sample_invoice.jpg")
        print("=" * 60 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample image: {str(e)}")
        print("=" * 60 + "\n")
        return False

def test_modules():
    """Test if modules can be imported"""
    print("=" * 60)
    print("🧪 TESTING MODULE IMPORTS")
    print("=" * 60)
    
    try:
        from src.preprocessing import preprocess_image
        print("✅ preprocessing module imported successfully")
    except Exception as e:
        print(f"❌ preprocessing module error: {str(e)}")
        return False
    
    try:
        from src.ocr_engine import run_ocr
        print("✅ ocr_engine module imported successfully")
    except Exception as e:
        print(f"❌ ocr_engine module error: {str(e)}")
        return False
    
    try:
        from src.postprocessing import postprocess, save_json
        print("✅ postprocessing module imported successfully")
    except Exception as e:
        print(f"❌ postprocessing module error: {str(e)}")
        return False
    
    try:
        from src.pipeline import process_document
        print("✅ pipeline module imported successfully")
    except Exception as e:
        print(f"❌ pipeline module error: {str(e)}")
        return False
    
    print("=" * 60 + "\n")
    return True

def main():
    """Run all verification tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "OCR INVOICE SYSTEM - SETUP TEST" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Check imports
    imports_ok = check_imports()
    
    # Check file structure
    files_ok = check_file_structure()
    
    # Test module imports
    modules_ok = test_modules()
    
    # Create sample image (only if imports work)
    sample_ok = False
    if imports_ok:
        sample_ok = create_sample_image()
    
    # Final summary
    print("=" * 60)
    print("📋 SETUP VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Dependencies:     {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ File Structure:   {'PASS' if files_ok else 'FAIL'}")
    print(f"✅ Modules:          {'PASS' if modules_ok else 'FAIL'}")
    print(f"✅ Sample Data:      {'PASS' if sample_ok else 'SKIP (needs dependencies)'}")
    print("=" * 60)
    
    if imports_ok and files_ok and modules_ok:
        print("\n🎉 SETUP VERIFICATION COMPLETE!")
        print("\n📌 Next Step: Run the OCR pipeline with:")
        print("   python main.py\n")
        return 0
    else:
        print("\n⚠️  SETUP INCOMPLETE - Please fix the issues above")
        print("\nTo install missing dependencies, run:")
        print("   python -m pip install -r requirements.txt\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
