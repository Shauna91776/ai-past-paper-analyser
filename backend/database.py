# Connects Python to your PostgreSQL database
import os
from sqlmodel import SQLModel, create_engine, Session

# Local PostgreSQL connection string (update username/password/dbname as needed)
# Example: "postgresql://postgres:your_password@localhost:5432/past_paper_db"
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/past_paper_db"
)

# Create the database engine
# echo=True prints SQL statements to your terminal, which is great for debugging
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Creates all SQLModel tables in the database if they don't exist yet."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency that yields a database session for each request."""
    with Session(engine) as session:
        yield session