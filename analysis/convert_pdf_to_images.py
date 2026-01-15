import fitz  # PyMuPDF
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PDF_PATH = os.path.join(BASE_DIR, "final_submission", "Team_Eklavya_Submission_FINAL_ULTIMATE.pdf")
OUTPUT_DIR = os.path.join(BASE_DIR, "final_submission", "report_pages")

def convert_pdf_to_images():
    if not os.path.exists(PDF_PATH):
        print(f"Error: PDF not found at {PDF_PATH}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    # Open the PDF
    doc = fitz.open(PDF_PATH)
    
    print(f"Converting {len(doc)} pages...")
    
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)  # Load page
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for high quality (300 DPI approx)
        
        output_filename = f"page_{page_index + 1}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        pix.save(output_path)
        print(f"Saved: {output_filename}")

    doc.close()
    print("Conversion Complete!")

if __name__ == "__main__":
    convert_pdf_to_images()
