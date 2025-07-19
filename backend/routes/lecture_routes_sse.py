import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner, ItemHelpers
from agents import RawResponsesStreamEvent, AgentUpdatedStreamEvent, RunItemStreamEvent
from pydantic import BaseModel
from typing import List, Dict, Any
from my_agents.lecture_agent_sse import lecture_agent
from schemas.lecture_sse import LessonRequest, LectureOutput


router = APIRouter(prefix="/api/v1/sse_lecture", tags=["lectures"])

def create_sse_message(event_name: str, data: dict or str) -> str:
    if isinstance(data, dict):
        json_data = json.dumps(data)
    else:
        json_data = json.dumps({"message": data}, ensure_ascii=False)
    return f"event: {event_name}\ndata: {json_data}\n\n"
@router.get("/test")
async def test_endpoint():
    def simple_stream():
        yield create_sse_message("test", "Hello SSE")
        yield create_sse_message("test", "This is working")
        yield create_sse_message("done", "Test complete")
    
    return StreamingResponse(simple_stream(), media_type="text/event-stream")

@router.get("/generate")
async def generate_lecture(
    subject: str,
    grade: str, 
    lesson: str,
    reference_text: str,
    number_of_periods: int,
    minutes_per_period: int,
    special_instructions: str = None,
    example: str = None
):
    request_text = f"""
    - Môn học: {subject}
    - Lớp học: {grade}
    - Bài học: {lesson}
    - Văn bản tham khảo: {reference_text}
    - Số tiết học: {number_of_periods}
    - Thời lượng mỗi tiết: {minutes_per_period} phút
    """
    if special_instructions:
        request_text += f"\nSpecial Instructions: {special_instructions}"
    if example:
        request_text += f"\nExample: {example}"
    try:
        print(f"Starting agent with request: {request_text[:100]}...")
        result = Runner.run_streamed(lecture_agent, request_text)
        print("Agent runner initialized successfully")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        raise HTTPException(status_code=500, detail=f"Agent initialization failed: {str(e)}")

    async def event_stream():
        try:
            yield create_sse_message("start",{ 
                "message": f"Bắt đầu tạo bài giảng: {subject} - {grade} - {lesson}",
                "stage": "initializing"
            })

            yield create_sse_message("agent_update", f"Đang phân tích yêu cầu: {number_of_periods} tiết học, mỗi tiết {minutes_per_period} phút...")

            final_content = ""
            current_stage = "starting"

            async for event in result.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    # Extract actual text content from the response event
                    if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                        delta_text = event.data.delta
                        # Only send if delta_text is a simple string, not complex objects
                        if delta_text and isinstance(delta_text, str) and len(delta_text.strip()) > 0:
                            yield f"data: {json.dumps(delta_text)}\n\n"
                    # Remove fallback dots as they're not meaningful
                elif isinstance(event, AgentUpdatedStreamEvent):
                    agent_name = event.new_agent.name if hasattr(event.new_agent, 'name') else 'AI Agent'
                    if agent_name == 'lecture_agent':
                        yield create_sse_message("agent_update", "Đang suy nghĩ về cách tổ chức nội dung phù hợp...")
                    else:
                        yield create_sse_message("agent_update", "Đang chuyển sang bước tiếp theo...")
                elif isinstance(event, RunItemStreamEvent):
                    item = event.item
                    if item.type == "tool_call_item":
                        yield create_sse_message("tool_output", {"status": f"Đang tính toán xem dựa trên thời lượng {number_of_periods} tiết và {minutes_per_period} phút mỗi tiết thì nên xây dựng cấu trúc thế nào..."})
                    elif item.type == "tool_call_output_item":
                        # Don't send raw tool output - it contains technical details
                        # Instead send user-friendly message
                        yield create_sse_message("tool_output", {"status": "Đã xây dựng xong cấu trúc bài giảng với các hoạt động phù hợp"})
                    elif item.type == "run_item_output_item":
                        final_content = ItemHelpers.get_item_content(item)
                        yield create_sse_message("final_content", final_content)
            yield create_sse_message("completed", "Đã tạo bài giảng")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"An error occurred during streaming: {e}") 
            print(f"Full traceback: {error_details}")
            yield create_sse_message("error", f"Đã xảy ra lỗi trong quá trình tạo bài giảng: {str(e)}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")