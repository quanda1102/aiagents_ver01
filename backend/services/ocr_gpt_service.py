import base64
from typing import Tuple
from fastapi import UploadFile

def encode_image_to_base64(file: UploadFile) -> Tuple[str, str]:
    content = file.file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    mime_type = file.content_type  # e.g. "image/png"
    return f"data:{mime_type};base64,{encoded}", file.filename
