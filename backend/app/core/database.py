from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
# Default to SQLite for local development if Postgres is not available
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/cti_db")

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Actually try to connect to verify PostgreSQL is running
    with engine.connect() as conn:
        pass
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    # Fallback to SQLite if psycopg2/postgres connection fails during setup
    print(f"Warning: Failed to connect to Postgres. Falling back to SQLite. Error: {e}")
    
    # Check for custom SQLite path in environment, otherwise use default
    custom_sqlite_path = os.getenv("SQLITE_DB_PATH")
    if custom_sqlite_path:
        DB_PATH = os.path.abspath(custom_sqlite_path)
        DB_DIR = os.path.dirname(DB_PATH)
    else:
        # Default path: project-root/database/sqlite/cti_app.db
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        DB_DIR = os.path.join(BASE_DIR, "database", "sqlite")
        DB_PATH = os.path.join(DB_DIR, "cti_app.db")
    
    # Ensure the directory exists
    if DB_DIR and not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    print(f"Using SQLite database at: {DB_PATH}")
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
