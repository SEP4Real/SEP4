#!/usr/bin/env python3
import os
from PIL import Image

def convert_png_to_pdf(png_path):
    pdf_path = os.path.splitext(png_path)[0] + '.pdf'
    # Check if PDF already exists and is newer than PNG to avoid redundant conversions
    if os.path.exists(pdf_path) and os.path.getmtime(pdf_path) > os.path.getmtime(png_path):
        print(f"Skipping (already up to date): {pdf_path}")
        return
        
    try:
        with Image.open(png_path) as im:
            if im.mode in ("RGBA", "P"):
                # Convert RGBA/Palette image to RGB before saving as PDF
                im = im.convert("RGB")
            im.save(pdf_path, "PDF")
        print(f"Converted: {png_path} -> {pdf_path}")
    except Exception as e:
        print(f"Error converting {png_path}: {e}")

def main():
    # Base directory is Documentation relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    doc_dir = os.path.abspath(os.path.join(script_dir, '../../Documentation'))
    
    print(f"Scanning for PNG diagrams in: {doc_dir}")
    
    count = 0
    for root, dirs, files in os.walk(doc_dir):
        # Skip the guidelines directory to avoid converting resource PDFs or reference images
        if 'guidelines' in root:
            continue
        # Skip Python environment directories if present in subdirectories
        if '.venv' in root or 'node_modules' in root:
            continue
            
        for file in files:
            if file.lower().endswith('.png'):
                png_path = os.path.join(root, file)
                convert_png_to_pdf(png_path)
                count += 1
                
    print(f"Scanning complete. Processed {count} PNG files.")

if __name__ == '__main__':
    main()
