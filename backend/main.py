# FastAPI entrypoint (API routes)

import os
import tempfile
from backend.pdf_reader import extract_text_from_pdf
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlmodel import Session, select

from backend.database import create_db_and_tables, get_session, engine
from backend.models import SubjectScope, ExamPaper, ExamQuestion
from backend.parser import parse_past_paper_with_ai
from backend.analytics import get_high_yield_topics, get_questions_by_topic

app = FastAPI(
    title="Past Paper Analytics API",
    description="Local, privacy-focused API for extracting exam questions and analyzing high-yield topics.",
    version="1.0.0"
)

# Build an absolute path to avoid current-working-directory mismatches on Windows
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "raw_pdfs")

# Ensure directory exists safely on startup
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except OSError:
        pass

@app.on_event("startup")
def on_startup():
    """Automatically create database tables when the FastAPI server starts."""
    create_db_and_tables()


@app.get("/")
def read_root():
    """Health check endpoint to verify the API is running."""
    return {"status": "online", "message": "Past Paper Analytics API is running successfully."}

@app.post("/pdf/read/")
def read_uploaded_pdf(file: UploadFile = File(...)):

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        result = extract_text_from_pdf(temp_path)

        return {
            "filename": file.filename,
            "total_pages": result["total_pages"],
            "pages": result["pages"]
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF could not be read."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        file.file.close()


# --- SCOPE MANAGEMENT ENDPOINTS ---

@app.get("/scopes/", response_model=List[SubjectScope])
def get_all_scopes(session: Session = Depends(get_session)):
    """Retrieve all available curriculum topics/scopes stored in the database."""
    statement = select(SubjectScope)
    return session.exec(statement).all()


@app.post("/scopes/", response_model=SubjectScope)
def create_scope(scope: SubjectScope, session: Session = Depends(get_session)):
    """Add a new curriculum topic to the active scope dictionary."""
    session.add(scope)
    session.commit()
    session.refresh(scope)
    return scope


# --- PDF UPLOAD & EXTRACTION ENDPOINT ---

@app.post("/papers/upload/")
def upload_and_parse_paper(
    subject_name: str,
    term_or_grade: str,
    year: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Uploads a past paper PDF, fetches the active scope for the subject,
    runs local AI extraction via Ollama, and saves the questions to SQLite.
    """
    # Ensure directory exists recursively right before saving
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 1. Save the uploaded file locally using the absolute path join
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Fetch allowed topics for this subject from the database
    statement = select(SubjectScope).where(SubjectScope.subject_name == subject_name)
    scopes = session.exec(statement).all()
    
    if not scopes:
        raise HTTPException(
            status_code=400, 
            detail=f"No curriculum scope found for subject '{subject_name}'. Please populate scopes first."
        )
    
    allowed_topic_names = [scope.topic_name for scope in scopes]
    topic_name_to_id = {scope.topic_name: scope.id for scope in scopes}

    # 3. Parse PDF using Ollama + Instructor
    try:
        extraction_result = parse_past_paper_with_ai(file_path, allowed_topic_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {str(e)}")

    # 4. Save Exam Paper Metadata to Database
    db_paper = ExamPaper(
        title=extraction_result.paper_title,
        year=year,
        term_or_grade=term_or_grade,
        file_hash=file.filename  # In production, use a true file hash (e.g., MD5)
    )
    session.add(db_paper)
    session.commit()
    session.refresh(db_paper)

    # 5. Save Extracted Questions and link them to topics
    saved_questions_count = 0
    for q in extraction_result.questions:
        # Match AI's mapped topic back to its database ID
        topic_id = topic_name_to_id.get(q.mapped_topic)
        
        if not topic_id:
            # Fallback if AI slightly deviated or matched a similar name
            topic_id = scopes[0].id 

        db_question = ExamQuestion(
            exam_paper_id=db_paper.id,
            topic_id=topic_id,
            question_number=q.question_number,
            question_text=q.question_text,
            marks=q.marks,
            difficulty_rating=q.difficulty_rating
        )
        session.add(db_question)
        saved_questions_count += 1

    session.commit()

    return {
        "message": "Past paper successfully parsed and indexed!",
        "paper_id": db_paper.id,
        "paper_title": db_paper.title,
        "questions_indexed": saved_questions_count
    }


# --- ANALYTICS ENDPOINTS ---

@app.get("/analytics/high-yield", response_model=List[dict])
def get_high_yield_analytics(limit: int = 10, session: Session = Depends(get_session)):
    """Returns the top-ranked high-yield topics based on cumulative mark allocations."""
    return get_high_yield_topics(session, limit=limit)


@app.get("/analytics/topics/{topic_id}/questions", response_model=List[ExamQuestion])
def get_questions_for_topic(topic_id: int, session: Session = Depends(get_session)):
    """Retrieves all past paper questions associated with a specific topic for focused revision."""
    return get_questions_by_topic(session, topic_id=topic_id)