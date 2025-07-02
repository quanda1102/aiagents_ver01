from fastapi import APIRouter
from my_agents.controllers import multi_agent_controller

router = APIRouter()

router.include_router(multi_agent_controller.router, prefix="")
