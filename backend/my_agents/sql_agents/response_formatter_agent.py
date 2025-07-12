from my_agents.sql_agents.base_agent import BaseAgent

class ResponseFormatterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ResponseFormatterAgent"
        self.role = "Định dạng kết quả tổng hợp từ các agent khác"

    async def run(self, input_data, context):
        question = input_data.get("question", "")
        intent = input_data.get("intent")
        entities = input_data.get("entities", [])
        schema = input_data.get("schema")
        sql = input_data.get("sql", {})
        validation = input_data.get("validation")
        explanation = input_data.get("explanation")

        response = {
            "question": question,
            "intent": intent,
            "entities": entities,
            "schema": schema,
            "sql": sql.get("sql"),
            "reasoning": sql.get("reasoning"),
            "confidence": sql.get("confidence"),
            "database": sql.get("database"),
            "validation": validation,
            "explanation": explanation
        }

        return {
            "formattedResponse": response
        }
