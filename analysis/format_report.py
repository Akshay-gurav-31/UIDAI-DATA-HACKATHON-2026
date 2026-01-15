import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(qn(name), value)

def add_page_number(run):
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')

    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = "PAGE"

    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'separate')

    fldChar3 = create_element('w:fldChar')
    create_attribute(fldChar3, 'w:fldCharType', 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def format_report(input_path, output_path):
    doc = Document(input_path)

    # 1. & 6. Footer and Page Numbering
    for section in doc.sections:
        footer = section.footer
        # Clear existing footer content if any
        for p in footer.paragraphs:
            p.text = ""
        
        # Add Footer Text and Page Numbering
        # Standard: UIDAI Data Hackathon 2026 | Team Eklavya [Tab] Page
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Add Footer Text
        run_text = footer_p.add_run("UIDAI Data Hackathon 2026 | Team Eklavya    ")
        run_text.font.size = Pt(10)
        run_text.font.color.rgb = RGBColor(128, 128, 128) # Grey
        
        # Add Page Number
        run_num = footer_p.add_run()
        add_page_number(run_num)
        run_num.font.size = Pt(10)
        run_num.font.color.rgb = RGBColor(128, 128, 128)

    # 3. Bullets Correction and 4. Alignment
    for para in doc.paragraphs:
        # Remove double bullets
        if "• •" in para.text:
            para.text = para.text.replace("• •", "•")
        
        # Consistent alignment (Justified for body text, usually)
        if para.style.name.startswith('Normal'):
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 1. Section Page Break (Critical)
    # Target: "Ground Truth Verification (Sample Audit)"
    for para in doc.paragraphs:
        if "Ground Truth Verification (Sample Audit)" in para.text:
            # Ensure it starts on a new page
            para.paragraph_format.page_break_before = True

    # 5. Tables alignment and splitting
    for table in doc.tables:
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Prevent splitting across pages
        for row in table.rows:
            row.allow_break_across_pages = False

    doc.save(output_path)
    print(f"Formatted report saved to: {output_path}")

if __name__ == "__main__":
    input_file = r"c:\Users\aksha\Desktop\UIDIA HACKTHON\final_submission\Team_Eklavya_Submission_FINAL.docx"
    output_file = r"c:\Users\aksha\Desktop\UIDIA HACKTHON\final_submission\Team_Eklavya_Submission_V2.docx"
    format_report(input_file, output_file)
