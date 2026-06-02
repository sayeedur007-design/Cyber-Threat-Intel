import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def get_absolute_sqlite_url(url: str) -> str:
    """
    Resolves relative SQLite database URLs to absolute paths relative to
    the backend project root directory. This prevents creating duplicate
    database files depending on which directory command line tools are run.
    """
    if url.startswith("sqlite:///"):
        db_path = url[9:]
        # If the path is already absolute, return it as is
        if os.path.isabs(db_path) or db_path.startswith("/"):
            return url
        # Make path absolute relative to the 'backend' project root folder
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        abs_path = os.path.abspath(os.path.join(backend_dir, db_path))
        # Ensure parent directories exist
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        return f"sqlite:///{abs_path}"
    return url

# Retrieve DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite if DATABASE_URL is not set or empty
if not DATABASE_URL:
    sqlite_db_path = os.getenv("SQLITE_DB_PATH")
    if sqlite_db_path:
        DATABASE_URL = f"sqlite:///{sqlite_db_path}"
    else:
        DATABASE_URL = "sqlite:///cti_database.db"

# Replace obsolete postgres:// prefix with postgresql:// for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Ensure SQLite relative paths are absolute relative to backend root
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = get_absolute_sqlite_url(DATABASE_URL)

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Setup connect_args for SQLite
connect_args = {
    "check_same_thread": False
} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Setup engine parameters with production pooling configurations for PostgreSQL
engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True
}

# Only apply pool size and overflow parameters if it is not an in-memory or file-based SQLite db
if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,  # recycle connections after 30 minutes
        "pool_timeout": 30     # timeout after 30 seconds if pool is exhausted
    })

# Create standard SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

# Create SessionLocal for request-scoped database transactions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base class for models
Base = declarative_base()

def get_db():
    """Dependency provider for FastAPI requests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """
    Executes a simple SELECT 1 query to verify active connectivity
    to the database without modifying any tables or data.
    """
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True