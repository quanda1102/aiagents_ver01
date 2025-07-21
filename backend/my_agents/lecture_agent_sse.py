from agents import Agent, function_tool
from schemas.lecture_sse import LectureOutput, Activity
from typing import List

def _calculate_activities_impl(minutes_per_lesson: int) -> List[dict]:
    """
    Hàm tính toán và tạo danh sách các hoạt động dựa trên số phút mỗi tiết.
    Giả sử rằng cứ mỗi 15 phút sẽ có một hoạt động.
    """
    number_of_sub_activities = minutes_per_lesson // 5
    activities_table = []
    for i in range(number_of_sub_activities):
        activities_table.append({
            f"Hoạt động của giáo viên {i+1}": "Nội dung hoạt động của giáo viên",
            f"Hoạt động của học sinh {i+1}": "Nội dung hoạt động của học sinh"
        })
    return activities_table

def _create_lecture_impl(so_tiet_hoc: int, so_phut_moi_tiet: int, subject: str = "", grade: str = "", lesson: str = "", reference_text: str = "") -> LectureOutput:
    """
    Tạo một bài giảng hoàn chỉnh dựa trên số tiết học và số phút mỗi tiết.
    Hàm này sẽ tự động tính toán các hoạt động cho mỗi tiết.

    Args:
        so_tiet_hoc: Tổng số tiết học của bài giảng.
        so_phut_moi_tiet: Số phút cho mỗi tiết học.
        subject: Môn học
        grade: Lớp học  
        lesson: Bài học
        reference_text: Văn bản tham khảo

    Returns:
        Một đối tượng LectureOutput đã được tạo.
    """
    lecture_activities = []
    for i in range(so_tiet_hoc):
        # Tự động gọi _calculate_activities_impl để tính toán hoạt động
        activity_table = _calculate_activities_impl(so_phut_moi_tiet)
        activity = Activity(
            name=f"Tiết {i+1}: {lesson}" if lesson else f"Hoạt động cho tiết {i+1}",
            goals=f"Học sinh hiểu và áp dụng được kiến thức {subject} - {lesson}" if subject and lesson else "Mục tiêu của hoạt động này.",
            content=f"Nội dung chi tiết về {lesson} dựa trên tài liệu: {reference_text[:100]}..." if reference_text else "Nội dung chi tiết của hoạt động.",
            products=f"Sản phẩm học tập về {lesson}" if lesson else "Sản phẩm mong đợi từ học sinh sau hoạt động.",
            table=activity_table
        )
        lecture_activities.append(activity)

    lecture = LectureOutput(
        title=f"{subject} - {grade} - {lesson}" if all([subject, grade, lesson]) else "Bài giảng được tạo bởi AI",
        goals=f"Mục tiêu tổng thể: Học sinh nắm vững kiến thức {subject} ở {grade}, cụ thể là {lesson}" if all([subject, grade, lesson]) else "Mục tiêu tổng thể của bài giảng.",
        equipment="Máy chiếu, bảng trắng, bút lông, tài liệu tham khảo.",
        activities=lecture_activities
    )
    return lecture

@function_tool(name_override="create_lecture", description_override="Tạo bài giảng dựa trên số tiết học, số phút mỗi tiết và thông tin bài học")
def create_lecture(so_tiet_hoc: int, so_phut_moi_tiet: int, subject: str = "", grade: str = "", lesson: str = "", reference_text: str = "") -> LectureOutput:
    """
    Tạo một bài giảng hoàn chỉnh dựa trên số tiết học và số phút mỗi tiết.
    
    Args:
        so_tiet_hoc: Số tiết học
        so_phut_moi_tiet: Số phút mỗi tiết
        subject: Môn học (VD: Toán, Vật lý)
        grade: Lớp học (VD: Lớp 10, Lớp 11)
        lesson: Tên bài học cụ thể
        reference_text: Văn bản tham khảo để xây dựng nội dung
    """
    return _create_lecture_impl(so_tiet_hoc, so_phut_moi_tiet, subject, grade, lesson, reference_text)

instructions = """
Bạn là một chuyên gia giáo dục tạo bài giảng chi tiết. 

QUAN TRỌNG: BẠN PHẢI LUÔN SỬ DỤNG HÀM create_lecture ĐỂ TẠO BÀI GIẢNG!

Quy trình bắt buộc:
1. Đọc và phân tích thông tin đầu vào
2. Trích xuất các tham số: môn học, lớp, bài học, số tiết, số phút/tiết, tài liệu tham khảo
3. NGAY LẬP TỨC gọi hàm create_lecture() với tất cả tham số

KHÔNG ĐƯỢC viết bài giảng bằng text thuần túy. BẮT BUỘC phải dùng function tool.

Ví dụ đúng:
Input: "Tạo bài giảng Toán lớp 10 về phương trình bậc 2, 2 tiết 45 phút"
→ NGAY LẬP TỨC gọi: create_lecture(so_tiet_hoc=2, so_phut_moi_tiet=45, subject="Toán", grade="Lớp 10", lesson="Phương trình bậc 2", reference_text="")

TUYỆT ĐỐI không tự viết nội dung bài giảng - chỉ được dùng function tool!
"""

lecture_agent = Agent(
    name="lecture_agent",
    instructions=instructions,
    tools=[create_lecture],
    model="gpt-4o-mini",
)



