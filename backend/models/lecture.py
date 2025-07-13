from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from models import Base  # dùng chung Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    content = Column(JSON)
    grade_level = Column(String(50))
    subject = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    teacher = relationship("User", back_populates="lectures")
