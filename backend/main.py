import uuid
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import fastapi
from my_agents.routes.quiz_routes import router as quiz_router
from routes.user_routes import router as user_router
from routes.chat_routes import router as chat_router
from utils.pydantic_helper import format_validation_errors
from utils.serialization import ensure_serializable
from schemas.chat import ChatRequest, ChatResponse
agents_list = ["router_agent", "google_drive_agent", "chatting_agent"]

app = FastAPI(
    title="AI Agent Backend API",
    description="Backend API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include quiz routes
app.include_router(quiz_router)
app.include_router(chat_router)
app.include_router(user_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Xử lý lỗi validation cho request body."""
    formatted_errors = format_validation_errors(exc.errors())
    
    # Create user-friendly error message
    error_details = []
    for err in formatted_errors:
        error_details.append(f"Field '{err['field']}': {err['message']}")
    
    return JSONResponse(
        status_code=422,
        content={
            "response": f"Yêu cầu không hợp lệ: {'; '.join(error_details)}",
            "session_id": None,
            "validation_errors": formatted_errors  # Detailed errors for debugging
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)
