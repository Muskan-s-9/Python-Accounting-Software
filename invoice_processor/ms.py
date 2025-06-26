import fitz  # PyMuPDF
from PIL import Image
from r8n.pipelines import InvoicePipeline
from io import BytesIO
import sys
import os

def convert_pdf_with_fitz(pdf_path, zoom=2.0):
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)  # Zoom factor for better quality
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        images.append(image)

    return images

def extract_invoice_from_pdf(pdf_path):
    print(f"📥 Reading: {pdf_path}")
    images = convert_pdf_with_fitz(pdf_path)

    pipeline = InvoicePipeline()
    results = []

    for page_num, image in enumerate(images, start=1):
        print(f"\n📄 Processing Page {page_num}...")
        result = pipeline(image)
        results.append(result)
        for key, value in result.items():
            print(f"{key}: {value}")

    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python r8n_invoice_extractor_fitz.py path/to/invoice.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    extract_invoice_from_pdf(pdf_path)
