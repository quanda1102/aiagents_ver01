import base64
from typing import Tuple, List
from fastapi import UploadFile
from io import BytesIO
from pdf2image import convert_from_bytes
from openai import OpenAI

client = OpenAI()


def encode_image_to_base64(file: UploadFile) -> Tuple[str, str]:
    content = file.file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    mime_type = file.content_type
    return f"data:{mime_type};base64,{encoded}", file.filename


def encode_bytes_to_base64_image(image_bytes: bytes, content_type: str = "image/png") -> str:
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{base64_str}"


async def ocr_image_with_gpt(file: UploadFile) -> str:
    image_bytes = await file.read()
    return await ocr_bytes_with_gpt(image_bytes, file.content_type)


async def ocr_bytes_with_gpt(image_bytes: bytes, content_type: str = "image/png") -> str:
    base64_image = encode_bytes_to_base64_image(image_bytes, content_type)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hãy trích xuất toàn bộ văn bản trong ảnh sau bằng tiếng Việt nếu có:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_image,
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2048,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


async def ocr_pdf_with_gpt(file: UploadFile) -> List[dict]:
    try:
        pdf_bytes = await file.read()
        images = convert_from_bytes(pdf_bytes, dpi=200)

        results = []
        for idx, img in enumerate(images):
            buf = BytesIO()
            img.save(buf, format="PNG")
            image_bytes = buf.getvalue()

            text = await ocr_bytes_with_gpt(image_bytes)
            results.append({"page": idx + 1, "text": text})

        return results

    except Exception as e:
        return [{"page": 0, "text": f"Error: {str(e)}"}]
