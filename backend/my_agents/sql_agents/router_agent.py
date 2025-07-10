from dataclasses import dataclass
from my_agents.sql_agents.base_agent import BaseAgent
from my_agents.sql_agents.query_understanding_agent_oa import analyze_question, QueryUnderstandingOutput
from my_agents.sql_agents.schema_explorer_agent import SchemaExplorerAgent
from my_agents.sql_agents.sql_generator_agent import SqlGeneratorAgent
from my_agents.sql_agents.execution_validator_agent import ExecutionValidatorAgent
from my_agents.sql_agents.response_formatter_agent import ResponseFormatterAgent
from my_agents.sql_agents.agent_context import AgentContext
from services.semantic_cache_service import SemanticCacheService

@dataclass
class RunResult:
    output: dict

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "RouterAgent"
        self.role = "Điều phối luồng text-to-sql, có tích hợp semantic cache."

        # Khởi tạo các agent con và dịch vụ
        self.schema_agent = SchemaExplorerAgent()
        self.sql_agent = SqlGeneratorAgent()
        self.validator_agent = ExecutionValidatorAgent()
        self.formatter_agent = ResponseFormatterAgent()
        self.cache_service = SemanticCacheService()

    async def run(self, input_data, context):
        question = input_data.get("question")
        session_id = input_data.get("sessionId")
        ctx = AgentContext({ "sessionId": session_id })

        # --- Bước 1: Kiểm tra Semantic Cache ---
        cached_response = await self.cache_service.search_cache(question)
        if cached_response:
            return RunResult(output=cached_response)

        # --- Nếu không có cache, tiếp tục luồng xử lý ---

        # Bước 2: Phân tích câu hỏi
        query_understanding_output: QueryUnderstandingOutput = await analyze_question(question)

        # Bước 3: Khám phá schema
        schema = await self.schema_agent.process(question, ctx)

        # Bước 4: Tạo SQL
        sql_generation_result = await self.sql_agent.process({
            "intent": query_understanding_output.intent,
            "entities": query_understanding_output.entities,
            "schema_context": schema.get("schema_context"),
            "probes": [],
        }, ctx)

        sql_query = sql_generation_result.get("sql") if sql_generation_result else None
        if not sql_query:
            raise ValueError(f"Không thể tạo câu lệnh SQL từ input. Chi tiết: {sql_generation_result.get('error', 'Không có thông tin lỗi')}")

        # Bước 5: Xác thực và Thực thi SQL
        execution_result = await self.validator_agent.process({ "sql": sql_query }, ctx)

        # Bước 6: Định dạng kết quả cuối cùng
        final_result = await self.formatter_agent.process({
            "question": question,
            "sql": { "sql": sql_query },
            "execution_result": execution_result
        }, ctx)

        # --- Bước 7: Lưu kết quả vào cache cho lần sau ---
        if final_result and not final_result.get("cached"):
            await self.cache_service.add_to_cache(
                question=question,
                final_response=final_result.get("final_response"),
                debug_info=final_result.get("debug_info")
            )

        return RunResult(output=final_result)
