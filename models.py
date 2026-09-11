from sqlalchemy import Column, Integer, String, Text, Boolean, ARRAY, Float, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    main_tag = Column(String, nullable=False)
    sub_tag = Column(String, nullable=False, unique=True, index=True)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    qid = Column(String, unique=True, index=True, nullable=False)
    topic_id = Column(Integer, nullable=False)
    main_tag = Column(String, nullable=False)
    sub_tag = Column(String, nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {A: "...", B: "...", ...}
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D, or E
    explanation = Column(Text)
    source = Column(String, default="IndiaBix")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    time_limit_minutes = Column(Integer, nullable=False)
    marks_correct = Column(Float, nullable=False)
    marks_wrong = Column(Float, nullable=False, default=0.0)
    show_explanations = Column(Boolean, default=False)
    question_ids = Column(ARRAY(Integer), nullable=False)  # Locked random set
    share_slug = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, nullable=False, index=True)
    participant_name = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    score = Column(Float)
    answers = Column(JSON)  # {question_id: selected_option, ...}
