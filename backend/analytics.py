# High-yield mark aggregation queries

from sqlmodel import Session, select, func
from backend.models import ExamQuestion, SubjectScope

def get_high_yield_topics(session: Session, limit: int = 10) -> list[dict]:
    """
    Queries the database to calculate total cumulative marks and question counts 
    per topic, ranking them from highest-yield to lowest-yield.
    """
    # SQL query: Join ExamQuestion and SubjectScope, group by topic, and sum marks
    statement = (
        select(
            SubjectScope.topic_name,
            SubjectScope.subject_name,
            func.sum(ExamQuestion.marks).label("total_marks"),
            func.count(ExamQuestion.id).label("question_count")
        )
        .join(ExamQuestion, SubjectScope.id == ExamQuestion.topic_id)
        .group_by(SubjectScope.id, SubjectScope.topic_name, SubjectScope.subject_name)
        .order_by(func.sum(ExamQuestion.marks).desc())
        .limit(limit)
    )
    
    results = session.exec(statement).all()
    
    # Format the results into clean dictionaries for the API/Frontend
    high_yield_ranking = []
    for row in results:
        topic_name, subject_name, total_marks, question_count = row
        high_yield_ranking.append({
            "subject_name": subject_name,
            "topic_name": topic_name,
            "total_marks": total_marks or 0,
            "question_count": question_count or 0
        })
        
    return high_yield_ranking


def get_questions_by_topic(session: Session, topic_id: int) -> list[ExamQuestion]:
    """Retrieves all indexed past paper questions belonging to a specific topic for targeted revision."""
    statement = select(ExamQuestion).where(ExamQuestion.topic_id == topic_id)
    return session.exec(statement).all()