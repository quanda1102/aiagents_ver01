from pydantic import BaseModel

class DocumentRequest(BaseModel):
    raw_text: str
    file_name: str = "formatted_document.docx"