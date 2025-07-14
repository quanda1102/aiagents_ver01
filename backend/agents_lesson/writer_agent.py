from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
from config import config
from schemas.lecture import LectureStructure
import re

client = OpenAI(api_key=config.OPENAI_API_KEY)

def clean_json_markdown(text: str) -> str:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text

def flatten_activities(activities: dict) -> dict:
    return {
        key: (value.get("description") if isinstance(value, dict) else value)
        for key, value in activities.items()
    }

class WriterAgent:
    async def process(self, input: dict, history: dict, db: Session) -> dict:
        """Agent 3: Content Writer"""
        try:
            structure = history.get("structurer")
            if not structure:
                raise HTTPException(status_code=400, detail="Missing structure in history")

            section = input.get("section")  # Optional

            prompt = f"""
Viết nội dung chi tiết {'cho phần ' + section if section else 'cho toàn bộ bài giảng'}:
Structure: {structure}
Trả về định dạng JSON với nội dung đầy đủ.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            clean = clean_json_markdown(content)
            parsed = LectureStructure.parse_raw(clean)
            parsed.activities = flatten_activities(parsed.activities)

            return parsed.dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in WriterAgent: {str(e)}")
