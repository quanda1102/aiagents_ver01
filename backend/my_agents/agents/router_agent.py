from my_agents.agents.base_agent import BaseAgent
from my_agents.agents.agent_communication import AgentCommunication
from my_agents.agents.query_understanding_agent import QueryUnderstandingAgent
from my_agents.agents.schema_explorer_agent import SchemaExplorerAgent
from my_agents.agents.sql_generator_agent import SqlGeneratorAgent
from my_agents.agents.execution_validator_agent import ExecutionValidatorAgent
from my_agents.agents.explanation_agent import ExplanationAgent
from my_agents.agents.response_formatter_agent import ResponseFormatterAgent

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "RouterAgent"
        self.role = "Tổng hợp toàn bộ luồng multi-agent"

        self.query_agent = QueryUnderstandingAgent()
        self.schema_agent = SchemaExplorerAgent()
        self.sql_agent = SqlGeneratorAgent()
        self.validator_agent = ExecutionValidatorAgent()
        self.explanation_agent = ExplanationAgent()
        self.formatter_agent = ResponseFormatterAgent()

    async def run(self, input_data, context):
        question = input_data.get("question")
        session_id = input_data.get("sessionId")

        ctx = AgentContext({ "sessionId": session_id })

        # Bước 1: Phân tích câu hỏi
        query = await self.query_agent.process(question, ctx)

        # Bước 2: Khám phá schema
        schema = await AgentCommunication.query_cache_or_execute(question, ctx, self.schema_agent)

        # Bước 3: Sinh SQL
        sql = await self.sql_agent.process({
            "intent": query.get("intent"),
            "entities": query.get("entities"),
            "schema_context": schema.get("schema_context"),
            "probes": [],
        }, ctx)

        # Bước 4: Kiểm tra SQL
        validation = await self.validator_agent.process({ "sql": sql.get("sql") }, ctx)

        # Bước 5: Giải thích SQL
        explanation = await self.explanation_agent.process({ "sql": sql.get("sql") }, ctx)

        # Bước 6: Định dạng kết quả
        result = await self.formatter_agent.process({
            "question": question,
            "intent": query.get("intent"),
            "entities": query.get("entities"),
            "schema": schema.get("schema_context"),
            "sql": sql,
            "validation": validation,
            "explanation": explanation
        }, ctx)

        return result
