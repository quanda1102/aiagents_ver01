import asyncio
import httpx
import json
from agents import Agent, Runner, function_tool
from my_agents.config import config
from my_agents.sql_agents.router_agent import RouterAgent as TextToSqlRouterAgent, RunResult
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TEXT_TO_SQL_API_URL = f"http://localhost:{config['server']['port']}/text-to-sql-workflow"

@function_tool
async def text_to_sql_tool(question: str, session_id: str = None):
    """
    Sử dụng công cụ này cho bất kỳ câu hỏi nào liên quan đến việc truy vấn cơ sở dữ liệu,
    ví dụ: "doanh thu là bao nhiêu?", "hiển thị cho tôi tất cả người dùng", v.v.
    Công cụ này sẽ khởi chạy một quy trình nội bộ để chuyển đổi câu hỏi của bạn thành SQL và thực thi nó.
    """
    router = TextToSqlRouterAgent()
    result = await router.run({"question": question, "sessionId": session_id}, None)
    logger.debug(f"Result from text_to_sql_tool: {result}")
    return result

main_router_agent = Agent(
    name="MainQueryRouter",
    instructions=(
        "Bạn là một agent định tuyến thông minh. Nhiệm vụ của bạn là phân tích câu hỏi của người dùng. "
        "Nếu câu hỏi có vẻ như là một truy vấn cho cơ sở dữ liệu (ví dụ: hỏi về doanh thu, người dùng, dữ liệu, sản phẩm...), "
        "hãy sử dụng `text_to_sql_tool` để trả lời. "
        "Đối với các câu hỏi khác không liên quan đến dữ liệu trong cơ sở dữ liệu (ví dụ: chào hỏi, hỏi về chức năng của bạn), "
        "hãy trả lời một cách thân thiện và cho biết bạn có thể giúp truy vấn dữ liệu."
    ),
    model="gpt-4o-mini",
    tools=[text_to_sql_tool],
)

async def run_agents(user_input: str, session_id: str):
    logger.info(f"Đang xử lý câu hỏi: '{user_input}' cho session: {session_id}")

    final_response = await Runner.run(
        starting_agent=main_router_agent,
        input=user_input,
    )
    logger.debug(f"Raw final_response from Runner.run: {final_response}")

    if isinstance(final_response, dict) and "final_response" in final_response:
        logger.debug(f"Returning RunResult with dict output: {final_response}")
        return RunResult(output=final_response)
    elif isinstance(final_response, str):
        logger.debug(f"Returning RunResult with string output: {final_response}")
        return RunResult(output={"final_response": final_response})
    else:
        serialized_response = json.dumps(final_response, ensure_ascii=False)
        logger.debug(f"Returning RunResult with serialized output: {serialized_response}")
        return RunResult(output={"final_response": serialized_response})