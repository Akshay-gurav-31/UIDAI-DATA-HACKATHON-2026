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

def format_report_mechanical(input_path, output_path):
    doc = Document(input_path)

    # Pre-clean: Remove all existing footer content to ensure no stale data/repeat logos
    for section in doc.sections:
        footer = section.footer
        for p in footer.paragraphs:
            p.text = ""

    # 4. Page Numbering (Separate System, All Content Pages)
    # Bottom-right, Grey, Size 9/10, Numeric Only
    for section in doc.sections:
        footer = section.footer
        # If no paragraph exists, add one
        if not footer.paragraphs:
            footer.add_paragraph()
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        # Clear existing runs just to be safe
        for run in p.runs:
            run.text = ""
        
        run = p.add_run()
        add_page_number(run)
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(128, 128, 128)

    # 2. Footer Rule (LAST PAGE ONLY)
    # Text: UIDAI Data Hackathon 2026 | Team Eklavya (NO page numbers here)
    # We add a section break at the very end to isolate the last page footer
    # Note: doc.add_section() adds a section AFTER the content. 
    # To truly isolate the last page, we would need to know pagination.
    # Standard docx isolation: Insert a section break.
    
    # Check if we already have multiple sections. If not, add one for the footer.
    # To avoid changing content flow too much, we'll just use the last existing section
    # and set its footer to NOT link to previous, if there are multiple.
    # If only one section, we'll force a link-break logic but that requires 2+ sections.
    # Let's add a section break at the very end of the document.
    
    # doc.add_section() # This by default is a "Next Page" break.
    # If the document is already finalized, the last section is the last page.
    
    # Let's just target the LAST section available.
    last_section = doc.sections[-1]
    last_section.footer.is_linked_to_previous = False
    
    # Filter the last page footer
    # Paragraph 0 is for page numbers (Right).
    # We'll add Paragraph 1 for footer text (Left or Centered).
    footer_text_p = last_section.footer.add_paragraph("UIDAI Data Hackathon 2026 | Team Eklavya")
    footer_text_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in footer_text_p.runs:
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(128, 128, 128)

    # 3. Logo Rule (Title Page Only, center-aligned)
    # Find the first graphic/drawing and center it. 
    logo_found = False
    for para in doc.paragraphs:
        if 'Graphic' in para._p.xml or 'drawing' in para._p.xml:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            logo_found = True
            break
    
    # 1. Section Page Break (Critical)
    # Hard break before "Ground Truth Verification (Sample Audit)"
    for para in doc.paragraphs:
        if "Ground Truth Verification (Sample Audit)" in para.text:
            para.paragraph_format.page_break_before = True

    # 5. Bullet Sanitization
    # Replace "• •" with "•"
    for para in doc.paragraphs:
        if "• •" in para.text:
            para.text = para.text.replace("• •", "•")

    # 6. Table Mechanical Cleanup
    # Borders, Alignment (Center), No splitting
    for table in doc.tables:
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Ensure it has borders (Standard Grid)
        table.style = 'Table Grid'
        for row in table.rows:
            row.allow_break_across_pages = False

    # 7. Spacing & Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    doc.save(output_path)
    print(f"Mechanical formatting complete. Saved to: {output_path}")

if __name__ == "__main__":
    pwd = r"c:\Users\aksha\Desktop\UIDIA HACKTHON"
    input_file = os.path.join(pwd, "final_submission", "Team_Eklavya_Submission_FINAL.docx")
    output_file = os.path.join(pwd, "final_submission", "Team_Eklavya_Submission_FINAL_ENGINE.docx")
    format_report_mechanical(input_file, output_file)
