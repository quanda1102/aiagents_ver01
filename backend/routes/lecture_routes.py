from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from config import config
from models import Base
from schemas.lecture import LectureInput, LectureContext, LectureStructure, LectureOutput
from services.lecture_service import LectureService
from utils.auth import get_current_user
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from agents_lesson.router_agent import RouterAgent, LessonChatRequest, LessonChatResponse

# Kết nối CSDL
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo bảng
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1/lectures", tags=["lectures"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_teacher(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "TEACHER":
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user

@router.post("/upload", response_model=LectureContext)
async def upload_lecture(file: UploadFile = File(...), grade_level: str = Form(...), subject: str = Form(...), db: Session = Depends(get_db), current_user: dict = Depends(require_teacher)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    lecture_input = LectureInput(title=file.filename, raw_content=file_path, grade_level=grade_level, subject=subject)
    return await LectureService.collect_context(lecture_input, db)

@router.post("/create", response_model=LectureOutput)
async def create_lecture(lecture_input: LectureInput, db: Session = Depends(get_db), current_user: dict = Depends(require_teacher)):
    context = await LectureService.collect_context(lecture_input, db)
    structure = await LectureService.structure_lecture(context, lecture_input)
    content = await LectureService.write_content(structure)
    return LectureService.save_lecture(content, lecture_input, current_user["id"], db)

@router.post("/edit", response_model=LectureStructure)
async def edit_lecture(structure: LectureStructure, edit_request: str, db: Session = Depends(get_db), current_user: dict = Depends(require_teacher)):
    return await LectureService.edit_lecture(structure, edit_request)

@router.get("/{lecture_id}/export")
async def export_lecture(lecture_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_teacher)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id, Lecture.teacher_id == current_user["id"]).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    lecture_output = LectureOutput.from_orm(lecture)
    file_path = LectureService.export_lecture_to_docx(lecture_output)
    return FileResponse(file_path)

@router.post("/structure", response_model=LectureStructure)
async def generate_structure(
    input: LectureInput,
    context: LectureContext,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    return await LectureService.structure_lecture(context, input)

@router.post("/chat-lesson", response_model=LessonChatResponse)
async def chat_lesson(request: LessonChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(require_teacher)):
    router = RouterAgent()
    return await router.route(request, db)