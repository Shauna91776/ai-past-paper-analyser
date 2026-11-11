# Pydantic schemas for structured LLM data output

from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedQuestionSchema(BaseModel):
    """Schema for an individual exam question extracted by the local AI."""
    question_number: str = Field(description="The question identifier, e.g., 'Q1.1' or '2(b)'")
    question_text: str = Field(description="The full verbatim text of the exam question")
    marks: int = Field(description="The exact total mark allocation for this question")
    mapped_topic: str = Field(description="Must match one of the allowed topics provided in the prompt taxonomy")
    difficulty_rating: Optional[str] = Field(default="Medium", description="Estimated difficulty: Easy, Medium, or Hard")


class ExamPaperExtractionResult(BaseModel):
    """Schema representing an entire batch or paper's extracted questions."""
    paper_title: str = Field(description="The title or identifier of the exam paper")
    total_questions_extracted: int = Field(description="Total count of questions found in the text")
    questions: List[ExtractedQuestionSchema] = Field(description="List of all structured questions extracted from the paper")