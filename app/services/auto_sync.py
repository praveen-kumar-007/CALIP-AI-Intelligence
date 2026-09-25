from __future__ import annotations

import datetime
import os
import shutil
import threading
import time
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Case, Document
from app.services.longtail_scraper import (
    get_homepage_categories_and_cases,
    crawl_case_document_page,
    sync_catalog_to_database,
    harvest_all_longtail_hierarchy,
)
from app.services.pdf_ingest import process_and_ingest_pdf, ingest_local_pdf, INCOMING_DIR, DOWNLOADS_DIR

# Auto-sync state tracking
_SYNC_LOCK = threading.Lock()
_LAST_SYNC_TIME: datetime.datetime | None = None
_LAST_SYNC_RESULT: dict[str, Any] = {
    "status": "idle",
    "last_run": None,
    "new_cases_found": 0,
    "new_documents_found": 0,
    "auto_ingested_pdfs": 0,
    "incoming_files_processed": 0,
}
_BACKGROUND_THREAD: threading.Thread | None = None
_STOP_EVENT = threading.Event()


def scan_and_ingest_incoming_folder() -> list[dict[str, Any]]:
    """
    Watches `data/incoming/` folder for newly dropped PDFs or documents.
    Whenever a file arrives:
    1. Moves file to `data/downloads/` with safe hashed filename.
    2. Runs high-level advanced OCR and structural layout extraction.
    3. Stores clean text and RAG artifacts SEPARATELY in `data/ocr_extracted/`.
    4. Automatically chunks and embeds into vector store.
    5. Extracts legal entities into knowledge graph.
    """
    if not INCOMING_DIR.exists():
        return []
    incoming_files = [f for f in INCOMING_DIR.iterdir() if f.is_file() and not f.name.startswith(".")]
    
    if not incoming_files:
        return []

    print(f"[AutoAdjust] Found {len(incoming_files)} incoming document(s). Processing...")
    results = []

    for file_path in incoming_files:
        try:
            filename = file_path.name
            suffix = file_path.suffix.lower()

            if suffix == ".pdf":
                title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                res = ingest_local_pdf(
                    local_path=str(file_path),
                    title=f"Incoming: {title}",
                    document_type="Document",
                )
                print(f"[AutoAdjust] Successfully ingested incoming PDF: {filename} -> Doc ID: {res['document_id']}")
                results.append(res)
                try:
                    file_path.unlink()
                except Exception:
                    pass
            else:
                print(f"[AutoAdjust] Skipping unsupported file extension: {filename}")
        except Exception as exc:
            print(f"[AutoAdjust] Failed to process incoming file {file_path.name}: {exc}")

    return results


def check_for_updates_and_sync(auto_ingest_new_pdfs: bool = True) -> dict[str, Any]:
    """
    Auto-adjust & sync pipeline:
    1. Ingests all newly dropped files from the `data/incoming/` hot folder.
    2. Checks longtailcases.com for newly added cases, folders, or PDF documents.
    3. Synchronizes them to the relational database.
    4. Downloads, runs high-level OCR, and stores text separately.
    5. Re-indexes chunks and updates knowledge graph.
    """
    global _LAST_SYNC_TIME, _LAST_SYNC_RESULT

    with _SYNC_LOCK:
        start_time = datetime.datetime.now(datetime.timezone.utc)
        print(f"[AutoSync] Starting sync & auto-adjust check at {start_time.isoformat()}...")

        db = SessionLocal()
        new_cases_count = 0
        new_docs_count = 0
        ingested_count = 0
        incoming_processed_count = 0

        try:
            # 1. Check incoming hot-folder for user/system dropped files
            incoming_results = scan_and_ingest_incoming_folder()
            incoming_processed_count = len(incoming_results)

            # 2. Fetch current live homepage items from upstream
            live_items = get_homepage_categories_and_cases()
            existing_case_ids = {c.id for c in db.query(Case.id).all()}

            items_to_crawl = []
            for item in live_items:
                case_id = f"lt-{item['doc_id']}" if not item["is_pdf"] else f"mis-{item['doc_id']}"
                if case_id not in existing_case_ids:
                    items_to_crawl.append(item)
                    new_cases_count += 1

            if items_to_crawl:
                print(f"[AutoSync] Discovered {len(items_to_crawl)} new case items! Crawling hierarchy...")
                for item in items_to_crawl:
                    if not item["is_pdf"]:
                        c_data = crawl_case_document_page(item["doc_id"], case_label=item["title"], category=item["category"])
                        sync_catalog_to_database({"categories": {item["category"]: [c_data]}})

            # 3. Re-harvest catalog snapshot to capture newly added files in existing folders
            catalog = harvest_all_longtail_hierarchy(limit_cases=44)
            synced_docs = sync_catalog_to_database(catalog)

            # 4. Check if any new documents exist that need ingestion
            unprocessed_docs = db.query(Document).filter(
                Document.processing_status == "QUEUED",
                Document.original_pdf_url.isnot(None),
            ).limit(5).all()

            if auto_ingest_new_pdfs and unprocessed_docs:
                for doc in unprocessed_docs:
                    try:
                        print(f"[AutoSync] Auto-ingesting newly discovered PDF: {doc.title} ({doc.original_pdf_url})")
                        process_and_ingest_pdf(
                            pdf_url=doc.original_pdf_url,
                            title=doc.title,
                            document_id=doc.id,
                            case_id=doc.case_id,
                            court=doc.court,
                            document_type=doc.document_type,
                        )
                        ingested_count += 1
                    except Exception as e:
                        print(f"[AutoSync] Error ingesting {doc.id}: {e}")

            _LAST_SYNC_TIME = datetime.datetime.now(datetime.timezone.utc)
            _LAST_SYNC_RESULT = {
                "status": "success",
                "last_run": _LAST_SYNC_TIME.isoformat(),
                "duration_seconds": round((_LAST_SYNC_TIME - start_time).total_seconds(), 2),
                "incoming_files_processed": incoming_processed_count,
                "new_cases_found": new_cases_count,
                "new_documents_found": synced_docs,
                "auto_ingested_pdfs": ingested_count + incoming_processed_count,
                "total_cases_in_system": db.query(Case).count(),
                "total_documents_in_system": db.query(Document).count(),
            }
            print(f"[AutoSync] Sync finished successfully. Result: {_LAST_SYNC_RESULT}")
            return _LAST_SYNC_RESULT
        except Exception as exc:
            _LAST_SYNC_RESULT = {
                "status": "error",
                "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "error": str(exc),
            }
            print(f"[AutoSync] Error during sync: {exc}")
            return _LAST_SYNC_RESULT
        finally:
            db.close()


def _auto_sync_loop(interval_seconds: int = 60):
    """
    Background worker loop:
    Polls hot folder frequently (every 10s) and full upstream sync every interval_seconds.
    """
    print(f"[AutoSync] Background polling worker active (upstream interval: {interval_seconds}s).")
    seconds_counter = 0

    while not _STOP_EVENT.is_set():
        try:
            # Frequently check incoming hot folder
            scan_and_ingest_incoming_folder()

            # Upstream check every interval_seconds
            if seconds_counter >= interval_seconds:
                check_for_updates_and_sync(auto_ingest_new_pdfs=True)
                seconds_counter = 0
        except Exception as exc:
            print(f"[AutoSync Loop Error]: {exc}")

        # Sleep 5 seconds between incoming checks
        for _ in range(5):
            if _STOP_EVENT.is_set():
                break
            time.sleep(1)
        seconds_counter += 5


def start_auto_sync_worker(interval_seconds: int | None = None):
    global _BACKGROUND_THREAD, _STOP_EVENT
    if not settings.AUTO_SYNC_ENABLED:
        print("[AutoSync] Background auto-sync worker is disabled via AUTO_SYNC_ENABLED=false.")
        return
    if _BACKGROUND_THREAD is not None and _BACKGROUND_THREAD.is_alive():
        return
    _STOP_EVENT.clear()
    effective_interval = interval_seconds if interval_seconds is not None else settings.AUTO_SYNC_INTERVAL_SECONDS
    _BACKGROUND_THREAD = threading.Thread(
        target=_auto_sync_loop,
        args=(effective_interval,),
        daemon=True,
        name="CALIP-AutoSync-Worker",
    )
    _BACKGROUND_THREAD.start()


def get_sync_status() -> dict[str, Any]:
    return {
        "worker_running": _BACKGROUND_THREAD is not None and _BACKGROUND_THREAD.is_alive(),
        "last_sync": _LAST_SYNC_TIME.isoformat() if _LAST_SYNC_TIME else None,
        "last_result": _LAST_SYNC_RESULT,
    }

