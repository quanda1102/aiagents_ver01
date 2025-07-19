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

def _create_lecture_impl(so_tiet_hoc: int, so_phut_moi_tiet: int) -> LectureOutput:
    """
    Tạo một bài giảng hoàn chỉnh dựa trên số tiết học và số phút mỗi tiết.
    Hàm này sẽ tự động tính toán các hoạt động cho mỗi tiết.

    Args:
        so_tiet_hoc: Tổng số tiết học của bài giảng.
        so_phut_moi_tiet: Số phút cho mỗi tiết học.

    Returns:
        Một đối tượng LectureOutput đã được tạo.
    """
    lecture_activities = []
    for i in range(so_tiet_hoc):
        # Tự động gọi _calculate_activities_impl để tính toán hoạt động
        activity_table = _calculate_activities_impl(so_phut_moi_tiet)
        activity = Activity(
            name=f"Hoạt động cho tiết {i+1}",
            goals="Mục tiêu của hoạt động này.",
            content="Nội dung chi tiết của hoạt động.",
            products="Sản phẩm mong đợi từ học sinh sau hoạt động.",
            table=activity_table
        )
        lecture_activities.append(activity)

    lecture = LectureOutput(
        title="Tên bài giảng mẫu",
        goals="Mục tiêu tổng thể của bài giảng.",
        equipment="Máy chiếu, bảng trắng, bút lông.",
        activities=lecture_activities
    )
    return lecture

@function_tool(name_override="create_lecture", description_override="Tạo bài giảng dựa trên số tiết học và số phút mỗi tiết")
def create_lecture(so_tiet_hoc: int, so_phut_moi_tiet: int) -> LectureOutput:
    """
    Tạo một bài giảng hoàn chỉnh dựa trên số tiết học và số phút mỗi tiết.
    """
    return _create_lecture_impl(so_tiet_hoc, so_phut_moi_tiet)

instructions = """
Bạn là một chuyên gia trong lĩnh vực giáo dục, có nhiều năm kinh nghiệm trong việc thiết kế và phát triển bài giảng.
Nhiệm vụ của bạn là tạo ra các bài giảng chi tiết, phù hợp với đối tượng học sinh và mục tiêu giáo dục.

Khi tạo bài giảng, bạn cần:
1. Phân tích yêu cầu về môn học, lớp học, và nội dung bài học
2. Sử dụng các công cụ có sẵn để tính toán và tạo hoạt động phù hợp
3. Đảm bảo bài giảng có cấu trúc rõ ràng với mục tiêu, nội dung và sản phẩm cụ thể
4. Thiết kế các hoạt động tương tác giữa giáo viên và học sinh

Hãy sử dụng hàm create_lecture để tạo bài giảng dựa trên thông tin được cung cấp.
"""

lecture_agent = Agent(
    name="lecture_agent",
    instructions=instructions,
    tools=[create_lecture],
    model="gpt-4o-mini",
)



