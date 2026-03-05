import io
import pypdf
import docx

async def extract_text_from_file(file_content: bytes, filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    text = ""
    
    if ext == "pdf":
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif ext in ["docx", "doc"]:
        doc = docx.Document(io.BytesIO(file_content))
        text = "\n".join([para.text for para in doc.paragraphs])
    elif ext == "txt":
        text = file_content.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
        
    return text.strip()
