# models/__init__.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import các model để đảm bảo SQLAlchemy "nhìn thấy" chúng
from .user import User
from .lecture import Lecture
from .quiz import Quiz, QuizAttempt
