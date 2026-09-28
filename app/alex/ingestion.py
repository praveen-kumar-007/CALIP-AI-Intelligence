"""
ALEX Ingestion Module: File validation, cryptographic integrity, and metadata extraction.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import pymupdf as fitz
except ImportError:
    import fitz


@dataclass
class IngestionResult:
    is_valid: bool
    file_path: str
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    mime_type: str
    page_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


def calculate_sha256(file_path: str) -> str:
    """Computes the SHA-256 cryptographic hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def detect_file_type(file_path: str) -> str:
    """Verifies magic bytes for PDF and standard image formats."""
    with open(file_path, "rb") as f:
        header = f.read(16)

    if header.startswith(b"%PDF-"):
        return "application/pdf"
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return "image/webp"
    elif header.startswith(b"II*\x00") or header.startswith(b"MM\x00*"):
        return "image/tiff"
    else:
        return "application/octet-stream"


def ingest_and_validate_file(
    file_path: str,
    max_size_bytes: int = 150 * 1024 * 1024,  # 150MB
) -> IngestionResult:
    """
    Ingests and rigorously validates a candidate legal document file.
    Performs file existence, size, magic byte verification, SHA-256 calculation,
    and PyMuPDF integrity verification.
    """
    path_obj = Path(file_path)
    if not path_obj.exists() or not path_obj.is_file():
        return IngestionResult(
            is_valid=False,
            file_path=file_path,
            file_name=path_obj.name,
            file_size_bytes=0,
            sha256_hash="",
            mime_type="unknown",
            error_message=f"File does not exist or is not a regular file: {file_path}",
        )

    size = path_obj.stat().st_size
    if size == 0:
        return IngestionResult(
            is_valid=False,
            file_path=file_path,
            file_name=path_obj.name,
            file_size_bytes=0,
            sha256_hash="",
            mime_type="unknown",
            error_message="File is empty (0 bytes).",
        )

    if size > max_size_bytes:
        return IngestionResult(
            is_valid=False,
            file_path=file_path,
            file_name=path_obj.name,
            file_size_bytes=size,
            sha256_hash="",
            mime_type="unknown",
            error_message=f"File size ({size} bytes) exceeds limit of {max_size_bytes} bytes.",
        )

    mime_type = detect_file_type(file_path)
    file_hash = calculate_sha256(file_path)

    metadata: dict[str, Any] = {}
    page_count = 0

    if mime_type == "application/pdf":
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            metadata = {
                "format": doc.metadata.get("format", "PDF"),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "mod_date": doc.metadata.get("modDate", ""),
                "is_encrypted": doc.is_encrypted,
            }
            doc.close()
        except Exception as e:
            return IngestionResult(
                is_valid=False,
                file_path=file_path,
                file_name=path_obj.name,
                file_size_bytes=size,
                sha256_hash=file_hash,
                mime_type=mime_type,
                error_message=f"Corrupt or unreadable PDF: {str(e)}",
            )
    else:
        # Non-PDF or image
        metadata = {"file_type": mime_type}
        page_count = 1

    return IngestionResult(
        is_valid=True,
        file_path=file_path,
        file_name=path_obj.name,
        file_size_bytes=size,
        sha256_hash=file_hash,
        mime_type=mime_type,
        page_count=page_count,
        metadata=metadata,
    )
