import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from openai import OpenAI
from config import config
from schemas.lecture import LectureStructure

client = OpenAI(api_key=config.OPENAI_API_KEY)

class EditorAgent:
    async def process(self, input: dict, history: dict, db: Session) -> dict:
        """Agent 4: Editor"""
        try:
            # Lấy bài giảng từ history
            structure = history.get("writer") or history.get("structurer")
            if not structure:
                raise HTTPException(status_code=400, detail="Missing structure or content in history")

            edit_request = input.get("edit_request")
            if not edit_request:
                raise HTTPException(status_code=400, detail="Missing edit_request")

            prompt = f"""
Chỉnh sửa bài giảng theo yêu cầu: {edit_request}
Structure: {structure}
Trả về định dạng JSON với bài giảng đã chỉnh sửa.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )

            edited_content = response.choices[0].message.content.strip()

            # ✅ Xử lý nếu LLM trả về kết quả trong markdown ```json
            edited_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", edited_content.strip())

            return LectureStructure.parse_raw(edited_content).dict()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in EditorAgent: {str(e)}")
