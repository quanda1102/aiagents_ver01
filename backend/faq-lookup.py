personal_info = """Bạn là một Quân, một chuyên gia tư vấn của Knm Holdings, trong dự án này bạn phụ trách công việc hỗ trợ con người viết sách, quản lý tài liệu."""
def faq_look_up(question: str) -> str:
    """Look up the answer to a question from a FAQ"""
    if "ban la gi" in question.lower() or "la ai" in question.lower():
        return personal_info
    elif "xin chao" in question.lower() or "hello" in question.lower() or "hi" in question.lower():
        return "Hi my friend"
    else: return "no result"