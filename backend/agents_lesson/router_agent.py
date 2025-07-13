from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from agents_lesson.context_agent import ContextAgent
from agents_lesson.structurer_agent import StructurerAgent
from agents_lesson.writer_agent import WriterAgent
from agents_lesson.editor_agent import EditorAgent
from sqlalchemy.orm import Session
from config import config
import redis
import json
import uuid

# Redis client for storing history
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    decode_responses=True
)

class LessonChatRequest(BaseModel):
    agent_name: str
    input: Dict
    history: Optional[Dict] = None

class LessonChatResponse(BaseModel):
    response: Dict
    next_agent_name: Optional[str]
    status: str

class RouterAgent:
    def __init__(self):
        self.agents = {
            "context": ContextAgent(),
            "structurer": StructurerAgent(),
            "writer": WriterAgent(),
            "editor": EditorAgent()
        }
        self.agent_flow = {
            "context": "structurer",
            "structurer": "writer",
            "writer": "editor",
            "editor": None  # End of flow
        }

    async def route(self, request: LessonChatRequest, db: Session) -> LessonChatResponse:
        agent_name = request.agent_name
        if agent_name not in self.agents:
            raise HTTPException(status_code=400, detail=f"Invalid agent name: {agent_name}")

        # Lưu history vào Redis
        session_id = request.history.get("session_id") if request.history else str(uuid.uuid4())
        if request.history:
            redis_client.setex(f"lesson:{session_id}", 3600, json.dumps(request.history))

        # Gọi agent tương ứng
        agent = self.agents[agent_name]
        response = await agent.process(request.input, request.history or {}, db)

        # Cập nhật history
        history = request.history or {}
        history[agent_name] = response
        history["session_id"] = session_id
        redis_client.setex(f"lesson:{session_id}", 3600, json.dumps(history))

        # Xác định agent tiếp theo
        next_agent_name = self.agent_flow.get(agent_name)
        status = "waiting_user_confirmation" if next_agent_name else "done"

        return LessonChatResponse(
            response=response,
            next_agent_name=next_agent_name,
            status=status
        )