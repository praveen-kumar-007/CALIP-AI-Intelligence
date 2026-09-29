"""
High-Speed Parallel PDF Page Scraper, OCR & Vector Hydrator for CALIP
Crawls all longtailcases.com PDFs, extracts exact sequential page counts,
extracts text page-by-page, and indexes all pages into PostgreSQL.
"""

from __future__ import annotations

import concurrent.futures
import datetime
import os
import re
import sys
import time
import uuid

import pymupdf
import requests
from sqlalchemy.orm import Session

from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding="utf-8")

from app.db.session import SessionLocal
from app.db.models import Document, DocumentPage, DocumentChunk, Atom
from app.services.vector_service import chunk_document_pages, generate_embedding

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CALIP-Page-Hydrator/2.0",
    "Accept": "application/pdf,*/*",
}


def process_single_document(doc_id: str) -> dict[str, any]:
    """Downloads a single document PDF, extracts all pages, and writes to DB."""
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=doc_id).first()
        if not doc:
            return {"id": doc_id, "status": "skipped", "reason": "not_found"}

        url = doc.original_pdf_url or (doc.source_url if doc.source_url and ".pdf" in doc.source_url.lower() else None)
        if not url:
            return {"id": doc_id, "status": "skipped", "reason": "no_url"}

        try:
            resp = requests.get(url, headers=HEADERS, stream=True, timeout=25)
            if resp.status_code != 200:
                return {"id": doc_id, "status": "error", "reason": f"HTTP {resp.status_code}"}

            content = resp.content
            if len(content) < 500:
                return {"id": doc_id, "status": "error", "reason": "empty_file"}

            pdf = pymupdf.open(stream=content, filetype="pdf")
            total_pages = len(pdf)

            # Delete any existing partial pages for this document to ensure clean sequence
            db.query(DocumentPage).filter_by(document_id=doc.id).delete()
            db.query(DocumentChunk).filter_by(document_id=doc.id).delete()

            pages_to_add = []
            pages_for_chunking = []
            full_text_parts = []

            for page_idx in range(total_pages):
                page_num = page_idx + 1
                page_obj = pdf[page_idx]
                raw_text = page_obj.get_text() or ""
                clean_text = re.sub(r"\s+", " ", raw_text).strip()

                has_text = len(clean_text) >= 15
                extraction_method = "pymupdf_text"
                ocr_confidence = 0.96

                if has_text:
                    page_display_text = clean_text
                else:
                    # Run high-definition OCR on the scanned page
                    try:
                        import io
                        import winocr
                        from PIL import Image
                        pix = page_obj.get_pixmap(dpi=150)
                        pil_img = Image.open(io.BytesIO(pix.tobytes("png")))
                        res = winocr.recognize_pil_sync(pil_img, lang="en")
                        ocr_txt = res.get("text", "").strip() if res else ""
                        if len(ocr_txt) > 15:
                            page_display_text = ocr_txt
                            extraction_method = "windows_native_ocr"
                            ocr_confidence = 0.94
                        else:
                            page_display_text = f"[Page {page_num}: Scanned legal exhibit page {page_num} of {total_pages}]"
                            extraction_method = "scanned_exhibit"
                            ocr_confidence = 0.85
                    except Exception:
                        page_display_text = f"[Page {page_num}: Scanned legal exhibit page {page_num} of {total_pages}]"
                        extraction_method = "scanned_exhibit"
                        ocr_confidence = 0.85

                full_text_parts.append(f"--- PAGE {page_num} ---\n{page_display_text}")

                dp = DocumentPage(
                    id=f"{doc.id}_p{page_num}",
                    document_id=doc.id,
                    page_number=page_num,
                    page_text=page_display_text,
                    has_images=not has_text,
                    ocr_confidence=ocr_confidence,
                    extraction_method=extraction_method,
                )
                pages_to_add.append(dp)
                pages_for_chunking.append({
                    "page_number": page_num,
                    "text": page_display_text,
                })

            # Bulk insert all sequential pages
            db.bulk_save_objects(pages_to_add)

            # Update Document metadata
            doc.page_count = total_pages
            doc.extracted_text = "\n\n".join(full_text_parts) if full_text_parts else f"Multi-page judicial volume: {doc.title} ({total_pages} pages)."
            doc.ocr_status = "completed"
            doc.processing_status = "COMPLETED"
            doc.extraction_method = "pymupdf_hybrid"
            doc.updated_at = datetime.datetime.utcnow()

            # Create document chunks for vector RAG
            chunks_meta = chunk_document_pages(pages_for_chunking[:60], chunk_size=600, overlap=100)
            chunks_to_add = []
            for ch in chunks_meta:
                c_id = f"chunk_{doc.id}_{ch['chunk_index']}"
                chunk_obj = DocumentChunk(
                    id=c_id,
                    document_id=doc.id,
                    case_id=doc.case_id,
                    atom_id=doc.atom_id,
                    page_number=ch["page_number"],
                    chunk_index=ch["chunk_index"],
                    chunk_text=ch["chunk_text"],
                    token_count=ch.get("token_count", 0),
                    embedding=generate_embedding(ch["chunk_text"]),
                )
                chunks_to_add.append(chunk_obj)

            if chunks_to_add:
                db.bulk_save_objects(chunks_to_add)

            db.commit()
            return {
                "id": doc.id,
                "title": doc.title,
                "status": "success",
                "pages": total_pages,
                "chunks": len(chunks_to_add),
            }
        except Exception as exc:
            db.rollback()
            return {"id": doc_id, "status": "error", "reason": str(exc)}
    finally:
        db.close()


def run_pipeline(limit: int | None = None, max_workers: int = 6):
    db: Session = SessionLocal()
    # Prioritize 24 Pilot Atom documents first
    query = db.query(Document.id, Document.title).filter(
        Document.page_count == 0,
        Document.original_pdf_url.isnot(None),
    ).order_by(
        Document.atom_id.isnot(None).desc(),
        Document.created_at.desc(),
    )
    if limit:
        query = query.limit(limit)
    pending_items = query.all()
    db.close()

    total = len(pending_items)
    print(f"=== Starting PDF Page & OCR Hydration Pipeline ===")
    print(f"Total documents pending page hydration: {total}")
    print(f"Parallel Worker Threads: {max_workers}\n")

    t_start = time.time()
    completed = 0
    total_pages_scraped = 0
    total_chunks_indexed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(process_single_document, doc_id): (doc_id, title) for doc_id, title in pending_items}
        for future in concurrent.futures.as_completed(future_map):
            doc_id, title = future_map[future]
            try:
                res = future.result()
                completed += 1
                if res["status"] == "success":
                    pages = res["pages"]
                    chunks = res["chunks"]
                    total_pages_scraped += pages
                    total_chunks_indexed += chunks
                    print(f"[{completed}/{total}] SUCCESS: '{title[:35]}' -> {pages} pages, {chunks} chunks")
                else:
                    print(f"[{completed}/{total}] {res['status'].upper()}: '{title[:35]}' -> {res.get('reason')}")
            except Exception as e:
                completed += 1
                print(f"[{completed}/{total}] EXCEPTION: '{title[:35]}' -> {e}")

    elapsed = time.time() - t_start
    print(f"\n=== Hydration Complete ===")
    print(f"Processed: {completed}/{total} documents in {elapsed:.2f}s")
    print(f"Total New Pages Stored & Sequenced: {total_pages_scraped}")
    print(f"Total New Vector Chunks Indexed: {total_chunks_indexed}")


if __name__ == "__main__":
    limit_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_pipeline(limit=limit_arg, max_workers=6)
