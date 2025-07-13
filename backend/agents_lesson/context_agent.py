import os
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
from config import config
from schemas.lecture import LectureContext
from services.lecture_service import LectureService

client = OpenAI(api_key=config.OPENAI_API_KEY)

class ContextAgent:
    async def process(self, input: dict, history: dict, db: Session) -> dict:
        """Agent 1: Context Collector"""
        try:
            # Lấy input
            raw_content = input.get("raw_content")
            grade_level = input.get("grade_level")
            subject = input.get("subject")

            if not raw_content or not grade_level or not subject:
                raise HTTPException(status_code=400, detail="Missing required fields: raw_content, grade_level, subject")

            # Trích xuất nếu là đường dẫn file
            if os.path.exists(raw_content):
                raw_content = LectureService.extract_file_content(raw_content)

            # JSON mẫu
            json_format = """
{
    "objectives": [],
    "skills": [],
    "activities": [],
    "equipment": [],
    "assessment": []
}
"""

            # Prompt
            prompt = f"""
Phân tích nội dung sau và trích xuất các thành phần:
- Mục tiêu bài học
- Kỹ năng cần đạt
- Hoạt động chính
- Thiết bị dạy học
- Đánh giá

Nội dung: {raw_content}
Khối lớp: {grade_level}
Môn học: {subject}

Trả về định dạng JSON:
{json_format}
"""

            # Gọi OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )

            context = response.choices[0].message.content.strip()

            # ✅ Loại bỏ ```json nếu có
            context = re.sub(r"^```(?:json)?\s*|\s*```$", "", context.strip())

            return LectureContext.parse_raw(context).dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in ContextAgent: {str(e)}")
