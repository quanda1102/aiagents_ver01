from my_agents.sql_agents.base_agent import BaseAgent
from my_agents.sql_agents.tools.database_tool import DatabaseTool

class ExecutionValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ExecutionValidatorAgent"
        self.role = "Xác thực, thực thi câu lệnh SQL và trả về kết quả."
        self.db_tool = DatabaseTool()

    async def run(self, input_data, context):
        sql = input_data.get("sql", "").strip()

        if not sql:
            return {
                "valid": False,
                "executed": False,
                "error": "Không có câu SQL để thực thi.",
                "data": None
            }

        # Bước 1: Xác thực câu lệnh SQL
        validation_result = self.db_tool.validate_sql(sql)
        if not validation_result.get("valid"):
            return {
                "valid": False,
                "executed": False,
                "error": f"Lỗi xác thực SQL: {validation_result.get('message')}",
                "data": None
            }

        # Bước 2: Thực thi câu lệnh SQL
        try:
            execution_result = self.db_tool.execute_sql(sql)
            if "error" in execution_result:
                return {
                    "valid": True,
                    "executed": False,
                    "error": f"Lỗi thực thi SQL: {execution_result.get('error')}",
                    "data": None
                }
            
            return {
                "valid": True,
                "executed": True,
                "error": None,
                "data": execution_result.get("data"),
                "row_count": execution_result.get("row_count")
            }
        except Exception as e:
            return {
                "valid": True, # Cú pháp đã được xác thực là đúng
                "executed": False,
                "error": f"Lỗi ngoại lệ khi thực thi SQL: {str(e)}",
                "data": None
            }

