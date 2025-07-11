import uuid
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
import uvicorn
from my_agents.sql_agents.router_agent import RunResult
from my_agents.my_agents import run_agents
from services.ai_memory import AIMemoryService
from my_agents.routes.quiz_routes import router as quiz_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

# Initialize services
ai_memory = AIMemoryService()

class ChatRequest(BaseModel):
    user_id: int
    user_name: str
    user_email: EmailStr
    user_phone: str
    user_address: str
    user_city: str
    user_state: str
    user_zip: str
    user_country: str 
    user_role: str
    session_id: str | None = None
    user_message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

app = FastAPI(
    title="AI Agent Backend API",
    description="Backend API for AI Agent system with quiz functionality",
    version="1.0.0"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include quiz routes
app.include_router(quiz_router, prefix="/api/v1", tags=["quiz"])

def format_validation_errors(errors):
    """Chuyển đổi lỗi của Pydantic thành thông báo thân thiện."""
    formatted_errors = []
    
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        invalid_value = error.get("input", "")
        
        formatted_errors.append({
            "field": field,
            "message": message,
            "invalid_value": invalid_value,
            "error_type": error["type"]
        })
    return formatted_errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Xử lý lỗi validation cho request body."""
    formatted_errors = format_validation_errors(exc.errors())
    error_details = [f"Field '{err['field']}': {err['message']}" for err in formatted_errors]
    return JSONResponse(
        status_code=422,
        content={
            "response": f"Yêu cầu không hợp lệ: {'; '.join(error_details)}",
            "session_id": None,
            "validation_errors": formatted_errors  # Detailed errors for debugging
        }
    )

def ensure_serializable(obj):
    """Đảm bảo đối tượng có thể serialize thành JSON."""
    if isinstance(obj, dict):
        return {k: ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif hasattr(obj, '__dict__'):
        return ensure_serializable(obj.__dict__)
    else:
        return str(obj)  # Chuyển đổi các đối tượng không serializable thành string

@app.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_response(request: ChatRequest) -> ChatResponse:
    """Main endpoint to handle user chat requests."""
    session_id = request.session_id or str(uuid.uuid4())
    request.session_id = session_id
    ai_memory.store_user_request(request.model_dump())
    
    try:
        result = await run_agents(user_input=request.user_message, session_id=session_id)
        
        # Debug: Log result for inspection
        logger.info(f"Result from run_agents: {result}")
        
        # Process result
        if isinstance(result, RunResult):
            output = result.output
            logger.debug(f"Extracted output from RunResult: {output}")
        else:
            output = result
            logger.debug(f"Result is not RunResult, using directly: {output}")
        
        # Ensure output is serializable
        serializable_output = ensure_serializable(output)
        
        # Convert final_response to JSON string
        ai_response = json.dumps(serializable_output, ensure_ascii=False)
        logger.info(f"Final ai_response (JSON): {ai_response}")
        
        # Store AI response
        ai_memory.store_assistant_response(request.user_id, session_id, ai_response)
        
        return ChatResponse(response=ai_response, session_id=session_id)
        
    except Exception as e:
        logger.error(f"Serious error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error occurred: {str(e)}")

@app.get("/", status_code=200, include_in_schema=False)
async def root():
    return {"message": "API server is running."}

if __name__ == "__main__":
    from my_agents.config import config
    port = int(config.get("server", {}).get("port", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
