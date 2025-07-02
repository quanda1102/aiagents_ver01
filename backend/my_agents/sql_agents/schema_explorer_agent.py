from my_agents.agents.base_agent import BaseAgent
from openai import OpenAI
from my_agents.config import config

openai = OpenAI(api_key=config["openai"]["apiKey"])

class SchemaExplorerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "SchemaExplorerAgent"
        self.role = "Khám phá cấu trúc cơ sở dữ liệu"

    async def run(self, question, context):
        if not question:
            question = "Hãy mô tả toàn bộ cấu trúc cơ sở dữ liệu."

        prompt = f"""
Giả sử bạn là một trợ lý cơ sở dữ liệu. Trả lời câu hỏi sau liên quan đến schema của cơ sở dữ liệu:

"{question}"

Chỉ trả lời dưới dạng mô tả dễ hiểu (text), KHÔNG trả về SQL.
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý hiểu biết về schema cơ sở dữ liệu."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.3,
        )

        answer = response.choices[0].message.content.strip()

        return {
            "question": question,
            "schema_context": answer,
            "raw_prompt": prompt,
            "raw_response": answer
        }
