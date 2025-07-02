from fastapi import APIRouter
from my_agents.controllers import conversation_history_controller

router = APIRouter()

router.include_router(conversation_history_controller.router, prefix="")
