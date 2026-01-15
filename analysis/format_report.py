import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Inches

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

def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    p._p = p._element = None

def format_report_final_polish(input_path, output_path):
    doc = Document(input_path)

    # 1. REMOVE EXCESSIVE GAPS (Mechanical Fix)
    # Delete paragraphs that are purely empty if they are consecutive
    i = 0
    paragraphs = doc.paragraphs
    while i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        if not p.text.strip():
            # Check if previous or next is also empty to avoid triple/quadruple gaps
            # We allow AT MOST one blank line between content
            if i > 0 and not doc.paragraphs[i-1].text.strip():
                delete_paragraph(p)
                continue # Re-check at same index
        i += 1

    # 2. FOOTER & PAGE NUMBERING (Last-Page Only Footer + Global Numbers)
    for section in doc.sections:
        footer = section.footer
        for p in footer.paragraphs:
            p.text = "" # Clean all existing

    # Add Global Page Numbers (Bottom Right)
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run()
        add_page_number(run)
        run.font.size = Pt(9) # Mandated size 9
        run.font.color.rgb = RGBColor(128, 128, 128) # Grey

    # Add Last-Page Only Footer Text (No trailing symbols)
    last_section = doc.sections[-1]
    last_section.footer.is_linked_to_previous = False
    
    # We want footer text on the left, page number on the right
    # To keep it professional, we'll use a new paragraph in the footer
    footer_text_p = last_section.footer.add_paragraph("UIDAI Data Hackathon 2026 | Team Eklavya")
    footer_text_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in footer_text_p.runs:
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(128, 128, 128)

    # 3. LOGO CENTERING (Title Page Only)
    logo_fixed = False
    for para in doc.paragraphs:
        if 'Graphic' in para._p.xml or 'drawing' in para._p.xml:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_fixed = True
            break # Only the first one

    # 4. SECTION PAGE BREAK & HEADING ALIGNMENT
    for para in doc.paragraphs:
        if "Ground Truth Verification (Sample Audit)" in para.text:
            para.paragraph_format.page_break_before = True
        
        # Heading-Content Proximity: Remove blank lines immediately following headings
        if para.style.name.startswith('Heading'):
            # Optimization: could check next para, but delete_paragraph loop above already handles this generally
            pass

    # 5. BULLET & TABLE FIXES
    for para in doc.paragraphs:
        if "• •" in para.text:
            para.text = para.text.replace("• •", "•")

    for table in doc.tables:
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table.style = 'Table Grid'
        for row in table.rows:
            row.allow_break_across_pages = False

    # 6. MARGINS
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    doc.save(output_path)
    print(f"Final polished report saved to: {output_path}")

if __name__ == "__main__":
    pwd = r"c:\Users\aksha\Desktop\UIDIA HACKTHON"
    input_file = os.path.join(pwd, "final_submission", "Team_Eklavya_Submission_FINAL.docx")
    output_file = os.path.join(pwd, "final_submission", "Team_Eklavya_Submission_FINAL_POLISHED.docx")
    format_report_final_polish(input_file, output_file)
