from my_agents.agents.base_agent import BaseAgent

class ExecutionValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ExecutionValidatorAgent"
        self.role = "Kiểm tra cú pháp và khả năng thực thi của câu SQL"

    async def run(self, input_data, context):
        sql = input_data.get("sql", "").strip()

        if not sql:
            return {
                "valid": False,
                "message": "Không có câu SQL để kiểm tra"
            }

        if sql.endswith(";"):
            return {
                "valid": True,
                "message": "SQL có thể hợp lệ về mặt cú pháp (chưa kiểm tra thực thi)"
            }
        else:
            return {
                "valid": False,
                "message": "SQL không kết thúc bằng dấu chấm phẩy (;)"
            }
