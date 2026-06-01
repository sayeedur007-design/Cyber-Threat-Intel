import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite if DATABASE_URL is missing or likely a docker-only address
if not DATABASE_URL or "postgres:5432" in DATABASE_URL:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "cti_database.db")
    DATABASE_URL = f"sqlite:///{db_path}"

# Railway PostgreSQL providers use the legacy 'postgres://' scheme; SQLAlchemy requires the explicit 'postgresql://' dialect specifier.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires disabling same-thread checks for multi-threaded FastAPI request contexts; unsupported by PostgreSQL.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Exposed as SQLALCHEMY_DATABASE_URL for external Alembic migration environment compatibility (env.py).
SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()