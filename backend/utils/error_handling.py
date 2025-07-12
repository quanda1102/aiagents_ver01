from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def format_validation_errors(errors):
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

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = format_validation_errors(exc.errors())
    error_details = [f"Field '{err['field']}': {err['message']}" for err in formatted_errors]
    return JSONResponse(
        status_code=422,
        content={
            "response": f"Yêu cầu không hợp lệ: {'; '.join(error_details)}",
            "session_id": None,
            "validation_errors": formatted_errors
        }
    )