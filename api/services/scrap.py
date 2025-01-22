from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document as docx_document
from odfdo import Document as odf_document
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text

def read_file(file_path):
    # Define a dictionary to map file extensions to extraction functions
    extension_to_function = {
        'pdf': extract_text_from_pdf,
        'docx': extract_text_from_docx,
        'doc': extract_text_from_docx,
        'txt': extract_text_from_txt,
        'odt': extract_text_from_odt,
        'html': extract_text_from_html,
        'htm': extract_text_from_html,
        'rtf': extract_text_from_rtf,
        'md': extract_text_from_md,
        'markdown': extract_text_from_md
    }
    
    # Get the file extension
    extension = file_path.split('.')[-1].lower()
    
    # Retrieve the function based on the file extension
    extract_function = extension_to_function.get(extension)
    
    if extract_function:
        return extract_function(file_path)
    else:
        raise ValueError("Unsupported file type")

def extract_text_from_pdf(file_path):
    return pdf_extract_text(file_path)

def extract_text_from_docx(file_path):
    doc = docx_document(file_path)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_text_from_odt(file_path):
    doc = odf_document(file_path)
    return doc.get_formatted_text()

def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')
        return soup.get_text(separator=" ")

def extract_text_from_rtf(file_path):
    with open(file_path, 'r') as file:
        rtf_text = file.read()
        doc = rtf_to_text(rtf_text)
        return doc

def extract_text_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
