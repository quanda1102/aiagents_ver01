import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from routes.quiz_routes import router as quiz_router
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.chat_routes import router as chat_router
from routes.lecture_routes import router as lecture_router
from routes.lecture_routes_sse import router as lecture_sse_router
from my_agents.exam_agents.unified_routes import unified_router
from utils.pydantic_helper import format_validation_errors
from routes.ocr_gpt_routes import router as ocr_ai_router
from routes.dox_formatter_routes import router as docx_formatter_router
from routes.lecture_docx_routes import router as lecture_docx_router
from routes.lecture_format_routes import router as lecture_format_router
from starlette.middleware.sessions import SessionMiddleware
from config import config
from services.redis_manager import redis_manager
from contextlib import asynccontextmanager
from database import log_pool_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting up AI Agent Backend API...")
    await redis_manager.initialize()
    print("Redis manager initialized successfully")
    
    # Log initial database pool status
    pool_status = log_pool_status()
    print(f"Database pool initialized: {pool_status}")
    
    yield  # This separates startup from shutdown
    
    # Shutdown code
    print("Shutting down AI Agent Backend API...")
    # Log final pool status
    final_pool_status = log_pool_status()
    print(f"Final database pool status: {final_pool_status}")
    # Add any cleanup code here if needed


app = FastAPI(
    title="AI Agent Backend API",
    description="Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# Add session middleware before routers
app.add_middleware(
    SessionMiddleware,
    secret_key=config.SESSION_SECRET_KEY,
    same_site='lax',
    https_only=False
)

# Include all routes
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(lecture_router)
app.include_router(unified_router)
app.include_router(ocr_ai_router)
app.include_router(docx_formatter_router)
app.include_router(lecture_docx_router)
app.include_router(lecture_format_router)
app.include_router(lecture_sse_router)

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
