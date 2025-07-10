import json
from datetime import datetime
import decimal
from openai import AsyncOpenAI
from my_agents.sql_agents.base_agent import BaseAgent
from my_agents.config import config

class ResponseFormatterAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.name = "ResponseFormatterAgent"
        self.role = "Chuyển đổi kết quả SQL thành câu trả lời tự nhiên cho người dùng."
        self.client = AsyncOpenAI(api_key=config["openai"]["api_key"])
        self.model = "gpt-4o-mini"

    async def run(self, input_data, context):
        question = input_data.get("question")
        sql_query = input_data.get("sql", {}).get("sql")
        execution_result = input_data.get("execution_result", {})

        if not execution_result or not execution_result.get("executed"):
            error_message = execution_result.get("error", "Lỗi không xác định.")
            final_response = f"Rất tiếc, tôi không thể thực thi truy vấn của bạn. Đã xảy ra lỗi: {error_message}"
            
            return {
                "final_response": final_response,
                "cached": False,
                "debug_info": input_data
            }

        data = execution_result.get("data")
        row_count = execution_result.get("row_count", 0)

        # Nếu không có dữ liệu trả về
        if row_count == 0:
            final_response = "Truy vấn đã được thực thi thành công nhưng không tìm thấy dữ liệu nào phù hợp."
            return {
                "final_response": final_response,
                "cached": False,
                "debug_info": input_data
            }

        # Hàm chuyển đổi Decimal và datetime để JSON serializable
        def json_default_serializer(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()  # Chuyển đổi datetime thành chuỗi ISO 8601
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        # Chuyển đổi dữ liệu thành chuỗi JSON để đưa vào prompt
        data_str = json.dumps(data, indent=2, ensure_ascii=False, default=json_default_serializer)

        # Tạo prompt cho LLM
        prompt = f"""
        Dựa vào thông tin dưới đây, hãy tạo một câu trả lời tự nhiên, thân thiện và chuyên nghiệp cho người dùng.
        Câu trả lời phải súc tích, đi thẳng vào vấn đề và trình bày dữ liệu một cách rõ ràng (có thể dùng markdown nếu cần).

        Câu hỏi của người dùng: "{question}"
        
        Câu lệnh SQL đã thực thi:
        ```sql
        {sql_query}
        ```

        Dữ liệu trả về từ cơ sở dữ liệu (dưới dạng JSON):
        ```json
        {data_str}
        ```

        Hãy tạo câu trả lời cuối cùng cho người dùng.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một trợ lý AI chuyên nghiệp, có nhiệm vụ diễn giải kết quả truy vấn SQL thành câu trả lời bằng ngôn ngữ tự nhiên cho người dùng."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            final_response = response.choices[0].message.content

            # Lưu kết quả vào context để cache sau này
            context.set("final_response", final_response)
            context.set("sql_query", sql_query)

            return {
                "final_response": final_response,
                "cached": False,  # Đây là lần chạy đầu tiên, chưa phải từ cache
                "debug_info": input_data
            }

        except Exception as e:
            final_response = f"Tôi đã lấy được dữ liệu nhưng gặp lỗi khi định dạng câu trả lời: {str(e)}"
            return {
                "final_response": final_response,
                "cached": False,
                "debug_info": input_data
            }
