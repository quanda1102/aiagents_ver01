from fastapi import APIRouter
from my_agents.controllers import semantic_cache_controller

router = APIRouter()

router.include_router(semantic_cache_controller.router, prefix="")
