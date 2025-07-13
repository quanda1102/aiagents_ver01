from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
from config import config
from schemas.lecture import LectureStructure
import re

client = OpenAI(api_key=config.OPENAI_API_KEY)

def strip_json_markers(text: str) -> str:
    return re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()

class StructurerAgent:
    async def process(self, input: dict, history: dict, db: Session) -> dict:
        try:
            context = history.get("context")
            if not context:
                raise HTTPException(status_code=400, detail="Missing context in history")

            grade_level = input.get("grade_level")
            subject = input.get("subject")
            title = input.get("title")

            json_format = """
{
    "title": "",
    "objectives": [],
    "knowledge_standards": [],
    "activities": {
        "warm_up": "",
        "knowledge_formation": "",
        "practice": "",
        "application": ""
    },
    "questions": [],
    "equipment": [],
    "assessment": []
}
"""

            prompt = f"""
Dựa trên context sau, tạo khung bài giảng theo chuẩn Bộ GD Việt Nam:

Context: {context}
Tiêu đề: {title}
Khối lớp: {grade_level}
Môn học: {subject}

Trả về định dạng JSON:
{json_format}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.5
            )

            structure_raw = response.choices[0].message.content.strip()
            clean_json = strip_json_markers(structure_raw)
            return LectureStructure.parse_raw(clean_json).dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in StructurerAgent: {str(e)}")
