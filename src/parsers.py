import pypdf
import io

def extract_text_from_pdf(file_bytes) -> str:
    """Reads uploaded PDF binary bytes and extracts raw text string securely with content checks."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_content = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
        extracted_string = "\n".join(text_content).strip()
        
        # Fallback Check: Agar page layout mil raha hai par text elements zero hain
        if not extracted_string:
            return "ERROR_SCANNED_IMAGE: Standard text stream not found in this PDF structure."
            
        return extracted_string
    except Exception as e:
        return f"Error parsing PDF file artifact: {str(e)}"