from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
try:
    from backend.config import settings
except ImportError:
    from config import settings
import logging

logger = logging.getLogger(__name__)

# Normalize database URL (e.g., Supabase / Heroku postgres:// -> postgresql://)
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database schema, indexes, and applies column migrations if needed."""
    try:
        Base.metadata.create_all(bind=engine)
        
        # Check and add missing columns dynamically
        with engine.connect() as conn:
            inspector = inspect(engine)
            if "inspections" in inspector.get_table_names():
                existing_cols = {col["name"] for col in inspector.get_columns("inspections")}
                needed_cols = {
                    "capacity": "NUMERIC(10, 4)",
                    "re": "NUMERIC(10, 4)",
                    "rct": "NUMERIC(10, 4)",
                    "ambient_temperature": "NUMERIC(10, 2)"
                }
                for col_name, col_type in needed_cols.items():
                    if col_name not in existing_cols:
                        conn.execute(text(f"ALTER TABLE inspections ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                        logger.info(f"Added column '{col_name}' to 'inspections' table.")

        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e
