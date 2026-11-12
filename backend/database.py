from sqlmodel import SQLModel, create_engine, Session

# SQLite database file stored locally in your project root
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# create_engine for SQLite requires connect_args for threading safety in FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Automatically creates the SQLite database file and tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency that provides a database session for FastAPI endpoints."""
    with Session(engine) as session:
        yield session