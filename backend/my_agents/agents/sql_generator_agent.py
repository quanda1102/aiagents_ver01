from my_agents.agents.base_agent import BaseAgent
from openai import OpenAI
from my_agents.config import config

openai = OpenAI(api_key=config["openai"]["apiKey"])

class SqlGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "SqlGeneratorAgent"
        self.role = "Sinh câu SQL từ intent + entities + schema"

    async def run(self, input_data, context):
        intent = input_data.get("intent", "")
        entities = input_data.get("entities", [])
        schema_context = input_data.get("schema_context", "")
        probes = input_data.get("probes", [])

        prompt = f"""
Bạn là một trợ lý chuyên viết SQL. Dựa trên thông tin sau:

- Ý định: {intent}
- Thực thể: {", ".join(entities)}
- Kiến thức schema: {schema_context}
- Probes (nếu có): {probes}

Hãy tạo câu SQL phù hợp với ngữ cảnh. Trả về kết quả dưới dạng JSON:

{{
  "sql": string,
  "reasoning": string,
  "confidence": number,
  "database": string
}}
"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                { "role": "system", "content": "Bạn là trợ lý tạo câu SQL từ thông tin ngữ nghĩa." },
                { "role": "user", "content": prompt.strip() }
            ],
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content.strip()

        try:
            import json
            parsed = json.loads(raw_text)
            parsed["raw_prompt"] = prompt
            parsed["raw_response"] = raw_text
            return parsed
        except Exception:
            return {
                "sql": None,
                "reasoning": None,
                "confidence": 0.0,
                "database": None,
                "error": "Không parse được JSON từ mô hình",
                "raw_prompt": prompt,
                "raw_response": raw_text
            }
