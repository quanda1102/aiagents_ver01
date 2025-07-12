def format_validation_errors(errors):
    """Chuyển đổi lỗi của Pydantic thành thông báo."""
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