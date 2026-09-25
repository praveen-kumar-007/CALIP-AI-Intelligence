from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=False)
else:
    load_dotenv(override=False)


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "on", "t")


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


def _get_float(key: str, default: float) -> float:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return float(val.strip())
    except ValueError:
        return default


def _get_list(key: str, default: list[str]) -> list[str]:
    val = os.getenv(key)
    if val is None:
        return default
    items = [item.strip() for item in val.split(",") if item.strip()]
    return items if items else default


class Settings:
    """Production-grade centralized configuration loaded from environment variables."""

    # Application & Environment
    APP_NAME: str = os.getenv("APP_NAME", "CALIP Legal Case & Document Intelligence Platform")
    APP_ENV: str = os.getenv("APP_ENV", "production")
    DEBUG: bool = _get_bool("DEBUG", False)
    IS_SERVERLESS: bool = _get_bool("SERVERLESS", False) or bool(
        os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    )
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = _get_int("PORT", 8000)
    CORS_ORIGINS: list[str] = _get_list("CORS_ORIGINS", ["*"])

    # Base URLs
    CANONICAL_URL: str = os.getenv("CANONICAL_URL", "https://longtailcases.com")
    LONGTAIL_BASE_URL: str = os.getenv("LONGTAIL_BASE_URL", "https://longtailcases.com")
    SCRAPER_USER_AGENT: str = os.getenv("SCRAPER_USER_AGENT", "CALIP-Legal-Intelligence/1.0 (Research Platform)")
    SCRAPER_TIMEOUT_SECONDS: int = _get_int("SCRAPER_TIMEOUT_SECONDS", 15)

    # Directories & Ephemeral Temp Storage (Cloud & Serverless Ready: No local data/ folder)
    PROJECT_ROOT: Path = BASE_DIR
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", str(Path(tempfile.gettempdir()) / "calip_temp")))
    DATA_DIR: Path = TEMP_DIR
    DOWNLOADS_DIR: Path = TEMP_DIR / "downloads"
    INCOMING_DIR: Path = TEMP_DIR / "incoming"
    OCR_STORAGE_DIR: Path = TEMP_DIR / "ocr_extracted"
    CATALOG_CACHE_PATH: Path = TEMP_DIR / "longtail_catalog_tree.json"
    STATIC_DIR: Path = Path(os.getenv("STATIC_DIR", str(BASE_DIR / "app" / "static")))
    TEMPLATES_DIR: Path = Path(os.getenv("TEMPLATES_DIR", str(BASE_DIR / "app" / "templates")))

    # Database: Supabase Cloud PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:CalipDB2026@db.qmnzsgnompkfdqtdadhy.supabase.co:5432/postgres",
    )

    # Auto-Sync & Real-Time Ingest
    AUTO_SYNC_ENABLED: bool = _get_bool("AUTO_SYNC_ENABLED", True)
    AUTO_SYNC_INTERVAL_SECONDS: int = _get_int("AUTO_SYNC_INTERVAL_SECONDS", 1800)
    INCOMING_POLL_INTERVAL_SECONDS: int = _get_int("INCOMING_POLL_INTERVAL_SECONDS", 5)

    # OCR & Layout Pipeline
    ENABLE_WINDOWS_OCR: bool = _get_bool("ENABLE_WINDOWS_OCR", True)
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")
    MY_OCR_COMMAND: str = os.getenv("MY_OCR_COMMAND", "")
    OCR_CONFIDENCE_THRESHOLD: float = _get_float("OCR_CONFIDENCE_THRESHOLD", 0.60)
    OCR_LANG: str = os.getenv("OCR_LANG", "eng")

    # Vector Search & Semantic Embeddings
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "auto")
    CHUNK_SIZE: int = _get_int("CHUNK_SIZE", 600)
    CHUNK_OVERLAP: int = _get_int("CHUNK_OVERLAP", 100)

    # RAG & Production LLM Providers (Groq, NVIDIA NIM, Gemini, Ollama)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "mistralai/mistral-nemotron")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Local Ollama Fallback Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_GENERATE_URL: str = os.getenv("OLLAMA_GENERATE_URL", f"{os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')}/api/generate")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:8b")
    RAG_TEMPERATURE: float = _get_float("RAG_TEMPERATURE", 0.1)
    RAG_TOP_K: int = _get_int("RAG_TOP_K", 4)
    RAG_TIMEOUT_SECONDS: int = _get_int("RAG_TIMEOUT_SECONDS", 30)

    # Serverless & Cloud Platform Detection (Vercel, AWS Lambda, Render)
    IS_SERVERLESS: bool = bool(
        os.getenv("VERCEL")
        or os.getenv("VERCEL_ENV")
        or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        or os.getenv("SERVERLESS")
    )

    def init_directories(self) -> None:
        """Ensure ephemeral runtime directories exist without writing to project workspace."""
        for directory in [
            self.TEMP_DIR,
            self.DOWNLOADS_DIR,
            self.INCOMING_DIR,
            self.OCR_STORAGE_DIR,
            self.STATIC_DIR,
        ]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass


settings = Settings()
settings.init_directories()
