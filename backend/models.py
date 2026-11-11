# SQLModel database tables (Scope, Papers, Questions)

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column
from pgvector.sqlalchemy import Vector

class SubjectScope(SQLModel, table=True):
    __tablename__ = "subject_scope"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    subject_name: str
    topic_name: str
    description: Optional[str] = None
    
    # Relationship back to questions
    questions: List["ExamQuestion"] = Relationship(back_populates="topic")


class ExamPaper(SQLModel, table=True):
    __tablename__ = "exam_papers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    year: int
    term_or_grade: str
    file_hash: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship back to questions
    questions: List["ExamQuestion"] = Relationship(back_populates="exam_paper")


class ExamQuestion(SQLModel, table=True):
    __tablename__ = "exam_questions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    exam_paper_id: int = Field(foreign_key="exam_papers.id")
    topic_id: int = Field(foreign_key="subject_scope.id")
    
    question_number: str
    question_text: str
    marks: int
    difficulty_rating: Optional[str] = None
    
    # Vector embedding for semantic search (using pgvector)
    # Note: Adjust dimension size (e.g., 1536) based on your local model's output
    embedding: Optional[list[float]] = Field(default=None, sa_column=Column(Vector(1536)))

    # Links back to parent tables
    exam_paper: ExamPaper = Relationship(back_populates="questions")
    topic: SubjectScope = Relationship(back_populates="questions")