from my_agents.sql_agents.base_agent import BaseAgent
from my_agents.sql_agents.tools.database_tool import DatabaseTool

class SchemaExplorerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "SchemaExplorerAgent"
        self.role = "Khám phá cấu trúc cơ sở dữ liệu"
        self.db_tool = DatabaseTool()

    async def run(self, question, context):
        try:
            schema = self.db_tool.get_schema()
            return {
                "question": question,
                "schema_context": schema,
            }
        except Exception as e:
            return {
                "question": question,
                "error": f"Không thể lấy schema từ CSDL: {str(e)}",
                "schema_context": None,
            }

