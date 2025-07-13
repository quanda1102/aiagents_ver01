import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
from config import config
from schemas.lecture import LectureStructure

client = OpenAI(api_key=config.OPENAI_API_KEY)

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

            # ✅ Xử lý nếu LLM trả về trong block markdown ```json ... ```
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())

            return LectureStructure.parse_raw(content).dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in WriterAgent: {str(e)}")
