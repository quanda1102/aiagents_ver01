from fastapi import APIRouter, UploadFile, File
from typing import List
from services.ocr_service import ocr_image

router = APIRouter(prefix="/api/v1/ocr", tags=["ocr"])

@router.post("/images", response_model=List[dict])
async def ocr_multiple_images(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            result = await ocr_image(file)
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": f"OCR failed: {str(e)}",
                "text": ""
            })
    return results