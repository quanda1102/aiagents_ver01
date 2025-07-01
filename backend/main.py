import json
import uuid
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError, EmailStr
import uvicorn
import fastapi
from dotenv import load_dotenv
import os
from my_agents import run_agents

load_dotenv()

user_request = """{
    "user_id": "1",
    "user_name": "Dang Anh Quan",
    "user_email": "dangquan@gmail.com",
    "user_phone": "0909090909",
    "user_address": "123 Nguyen Van Linh, Q9, TP.HCM",
    "user_city": "TP.HCM",
    "user_state": "Q9",
    "user_zip": "123456",
    "user_country": "Vietnam",
    "user_role": "admin",
    "session_id": "",
    "user_input": ""
}"""

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
    user_input: str  # Added user_input field

try:
    ChatRequest1 = ChatRequest.model_validate_json(user_request)
    print(ChatRequest1)
except ValidationError as e:
    print(f"Validation error: {e}")

class ChatResponse(BaseModel):
    response: str
    session_id: str

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_validation_errors(errors):
    """Convert Pydantic errors to user-friendly messages"""
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
    formatted_errors = format_validation_errors(exc.errors())
    error_details = [f"Field '{err['field']}': {err['message']}" for err in formatted_errors]
    return JSONResponse(
        status_code=422,
        content={
            "response": f"Request validation failed: {'; '.join(error_details)}",
            "session_id": None,
            "validation_errors": formatted_errors
        }
    )

@app.post("/chat", response_model=ChatResponse, status_code=200)
async def chat_response(request: ChatRequest) -> ChatResponse:
    response = ""
    async for event in run_agents(request.user_input):
        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
            response += event.data.delta
    return ChatResponse(response=response or "No response from agent", session_id=request.session_id or str(uuid.uuid4()))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)