from __future__ import annotations

import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

DATA_DIR = settings.DATA_DIR
DB_PATH = DATA_DIR / "calip.db"
DATABASE_URL = settings.DATABASE_URL
IS_SERVERLESS = getattr(settings, "IS_SERVERLESS", False) or bool(
    os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
)

# On serverless platforms (e.g. Vercel), root directory is read-only.
# If SQLite is used, copy bundled database to /tmp/calip.db to support writes and WAL.
if IS_SERVERLESS and DATABASE_URL.startswith("sqlite"):
    import tempfile
    tmp_dir = Path(tempfile.gettempdir())
    tmp_db = tmp_dir / "calip.db"
    bundled_db = settings.PROJECT_ROOT / "data" / "calip.db"
    if not tmp_db.exists() and bundled_db.exists():
        try:
            shutil.copy2(bundled_db, tmp_db)
        except Exception as exc:
            print(f"[Session] Warning copying db to temp directory: {exc}")
    if tmp_db.exists():
        DATABASE_URL = f"sqlite:///{tmp_db.as_posix()}"

connect_args = {"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        try:
            cursor.execute("PRAGMA busy_timeout=30000")
        except Exception:
            pass
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
