# tools.py
import os
import fitz  # PyMuPDF
from docx import Document
from docx2pdf import convert

def convert_pdf_to_docx(input_path, output_path):
    """Converts a PDF file to a DOCX file by extracting text."""
    try:
        if not os.path.exists(input_path):
            return False, "Input file not found."

        pdf_document = fitz.open(input_path)
        doc = Document()

        # Extract text from each page and add it to the Word document
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            doc.add_paragraph(text)

        doc.save(output_path)
        pdf_document.close()
        return True, f"Successfully converted to {output_path}"
    except Exception as e:
        return False, f"Error during PDF to DOCX conversion: {e}"

def convert_docx_to_pdf(input_path, output_path):
    """Converts a DOCX file to a PDF file."""
    try:
        if not os.path.exists(input_path):
            return False, "Input file not found."
            
        # Note: docx2pdf is a wrapper that may require MS Word (on Windows)
        # or LibreOffice (on Linux) to be installed.
        convert(input_path, output_path)
        return True, f"Successfully converted to {output_path}"
    except Exception as e:
        return False, f"Error during DOCX to PDF conversion: {e}. (Note: This may require Microsoft Word or LibreOffice to be installed.)"