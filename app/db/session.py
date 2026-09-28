from __future__ import annotations

import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

import re

def sanitize_database_url(url: str) -> str:
    """
    Sanitizes database URL for production and serverless (Vercel) environments:
    1. Ensures correct postgresql+psycopg2 driver prefix.
    2. Supabase IPv6 Fix: Direct host db.<ref>.supabase.co resolves to IPv6 which
       fails on Vercel AWS Lambda with 'Cannot assign requested address' (errno 99).
       Automatically rewrites direct host to the Supabase IPv4 Connection Pooler host.
    """
    if not url:
        return "sqlite:///:memory:"

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)

    # Supabase IPv6 direct-connection fix for Vercel/AWS Lambda
    match = re.search(r"@db\.([a-z0-9]+)\.supabase\.co(?::\d+)?", url)
    if match:
        project_ref = match.group(1)
        url = re.sub(
            r"://([^:@]+):([^@]+)@db\.[a-z0-9]+\.supabase\.co(?::\d+)?",
            lambda m: f"://{m.group(1)}.{project_ref}:{m.group(2)}@aws-0-ap-south-1.pooler.supabase.com:5432"
                      if not m.group(1).endswith(f".{project_ref}")
                      else f"://{m.group(1)}:{m.group(2)}@aws-0-ap-south-1.pooler.supabase.com:5432",
            url,
        )
        if "sslmode=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode=require"

    return url


DATABASE_URL = sanitize_database_url(settings.DATABASE_URL)

IS_SERVERLESS = getattr(settings, "IS_SERVERLESS", False) or bool(
    os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
)

connect_args = (
    {"check_same_thread": False, "timeout": 30}
    if DATABASE_URL.startswith("sqlite")
    else {"connect_timeout": 10}
)

if IS_SERVERLESS:
    from sqlalchemy.pool import NullPool
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        poolclass=NullPool,
        echo=False,
    )
else:
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
