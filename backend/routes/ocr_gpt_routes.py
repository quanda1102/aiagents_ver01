from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import openai
from config import config
from services.ocr_gpt_service import encode_image_to_base64

router = APIRouter(prefix="/api/v1/ocr-ai", tags=["ocr-ai"])

openai.api_key = config.OPENAI_API_KEY

@router.post("/images", response_model=List[dict])
async def ocr_images_with_gpt(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        try:
            base64_image, filename = encode_image_to_base64(file)

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Hãy trích xuất toàn bộ nội dung chữ trong ảnh dưới đây."},
                            {"type": "image_url", "image_url": {"url": base64_image}},
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
