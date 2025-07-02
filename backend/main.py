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
from my_agents.my_agents import run_agents
from services.ai_memory import AIMemoryService
import os
ai_memory = AIMemoryService()
load_dotenv(override=True)

# #Mock data for testing
# user_request = """{
#     "user_id": "1",
#     "user_name": "Dang Anh Quan",
#     "user_email": "dangquan@gmail.com",
#     "user_phone": "0909090909",
#     "user_address": "123 Nguyen Van Linh, Q9, TP.HCM",
#     "user_city": "TP.HCM",
#     "user_state": "Q9",
#     "user_zip": "123456",
#     "user_country": "Vietnam",
#     "user_role": "admin",
#     "session_id": "",
#     "user_message": "I want to create a new document in Google Drive"
# }"""
# print(user_request)

class ChatRequest(BaseModel):
    user_id: str
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
    ai_memory.store_user_request(request.model_dump())
    try:
        ai_response = await run_agents(f"User message: {request.user_message} \n\n Chat history: {ai_memory.get_formatted_chat_history(request.user_id, request.session_id, max_history=10)}")
        ai_memory.store_assistant_response(request.user_id, request.session_id, ai_response)
        return ChatResponse(response=ai_response, session_id=request.session_id or str(uuid.uuid4()))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)