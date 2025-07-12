from my_agents.sql_agents.base_agent import BaseAgent
from openai import OpenAI
from my_agents.config import config

openai = OpenAI(api_key=config["openai"]["apiKey"])

class ExplanationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ExplanationAgent"
        self.role = "Giải thích lý do và ý nghĩa của câu SQL"

    async def run(self, input_data, context):
        sql = input_data.get("sql", "").strip()

        if not sql:
            return { "explanation": "Không có câu SQL để giải thích." }

        prompt = f"""
Hãy giải thích ý nghĩa của câu SQL sau đây một cách dễ hiểu cho người dùng không chuyên:

```sql
{sql}
```

"""

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                { "role": "system", "content": "Bạn là một trợ lý giải thích SQL cho người không chuyên." },
                { "role": "user", "content": prompt.strip() }
            ],
            temperature=0.3,
        )

        explanation = response.choices[0].message.content.strip()

        return {
            "sql": sql,
            "explanation": explanation,
            "raw_prompt": prompt,
            "raw_response": explanation,
        }