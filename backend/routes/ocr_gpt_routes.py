from fastapi import APIRouter, UploadFile, File
from typing import List
from config import config
from services import ocr_gpt_service as ocr

from openai import OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY)

router = APIRouter(prefix="/api/v1/ocr-ai", tags=["ocr-ai"])


@router.post("/images", response_model=List[dict])
async def ocr_images_with_gpt(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            base64_image, filename = ocr.encode_image_to_base64(file)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Hãy trích xuất toàn bộ nội dung chữ trong ảnh dưới đây."},
                            {"type": "image_url", "image_url": {"url": base64_image, "detail": "high"}},
                        ],
                    }
                ],
                max_tokens=2048,
            )

            text = response.choices[0].message.content.strip()
            results.append({"filename": filename, "text": text})

        except Exception as e:
            results.append({"filename": file.filename, "text": f"Error: {str(e)}"})

    return results


@router.post("/pdf", response_model=dict)
async def ocr_pdf(file: UploadFile = File(...)):
    pages = await ocr.ocr_pdf_with_gpt(file)
    return {"filename": file.filename, "pages": pages}
