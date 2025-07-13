from pydantic import BaseModel
from typing import Optional, Dict, List

class LectureInput(BaseModel):
    title: str
    raw_content: str  # Nội dung thô hoặc đường dẫn file
    grade_level: str
    subject: str
    objectives: Optional[List[str]] = None
    skills: Optional[List[str]] = None

class LectureContext(BaseModel):
    objectives: List[str]
    skills: List[str]
    activities: List[str]
    equipment: List[str]
    assessment: List[str]

class LectureStructure(BaseModel):
    title: str
    objectives: List[str]
    knowledge_standards: List[str]
    activities: Dict[str, str]  # Khởi động, hình thành kiến thức, luyện tập, vận dụng
    questions: List[str]
    equipment: List[str]
    assessment: List[str]

class LectureOutput(BaseModel):
    id: int
    teacher_id: int
    title: str
    content: Dict
    grade_level: str
    subject: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True