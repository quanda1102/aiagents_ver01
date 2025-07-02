from my_agents.agents.base_agent import BaseAgent
from openai import OpenAI
from my_agents.config import config

openai = OpenAI(api_key=config["openai"]["apiKey"])

class QueryUnderstandingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "QueryUnderstandingAgent"
        self.role = "Phân tích ngữ nghĩa câu hỏi người dùng"

    async def run(self, question, context):
        if not question:
            return {
                "intent": None,
                "entities": [],
                "message": "Không có câu hỏi để phân tích"
            }

        prompt = f"""
Bạn là một agent hiểu ngữ nghĩa câu hỏi. Hãy phân tích câu hỏi sau:

"{question}"

Trả lời bằng JSON có dạng:
{{
  "intent": string,
  "entities": string[]
}}
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là một agent hiểu ngữ nghĩa câu hỏi và trích xuất intent + entities."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content.strip()

        try:
            import json
            parsed = json.loads(raw_text)
            return {
                "intent": parsed.get("intent"),
                "entities": parsed.get("entities", []),
                "raw_prompt": prompt,
                "raw_response": raw_text
            }
        except Exception:
            return {
                "intent": None,
                "entities": [],
                "error": "Không phân tích được JSON",
                "raw_response": raw_text,
                "raw_prompt": prompt
            }
