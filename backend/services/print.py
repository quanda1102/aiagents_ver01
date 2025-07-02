from ai_memory import AIMemoryService


ai_memory = AIMemoryService()


user_request_data = {
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
        "session_id": "2",
        "user_message": "hiiiii, heloo are you goodooo"
    }




ai_memory.get_formatted_chat_history(user_id="1", session_id="3", max_history=20)

