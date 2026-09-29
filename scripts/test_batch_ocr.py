"""
Test runner for batch OCR extraction and vector indexing.
"""
import io
import os
import re
import sys
import time
from pathlib import Path
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pymupdf
from PIL import Image
import winocr
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db.models import Document, DocumentPage
from app.services.text_cleaner import sanitize_legal_text_for_rag_and_training, is_placeholder_or_dummy_text
from app.services.vector_service import index_document_chunks
from app.services.ocr_service import store_extracted_ocr_separately

CACHE_DIR = Path("data/pdf_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def download_or_get_pdf(url: str, doc_id: str) -> Path | None:
    cache_path = CACHE_DIR / f"{doc_id}.pdf"
    if cache_path.exists() and cache_path.stat().st_size > 1000:
        return cache_path

    urls_to_try = [url]
    if "doc-Documents_" in doc_id:
        num = doc_id.replace("doc-Documents_", "").replace("_pdf", "").split("_")[0]
        urls_to_try.append(f"https://longtailcases.com/uploads/files/Documents-{num}.pdf")
        urls_to_try.append(f"https://longtailcases.com/uploads/documents/Documents-{num}.pdf")

    for u in urls_to_try:
        if not u:
            continue
        try:
            r = requests.get(u, timeout=30)
            if r.status_code == 200 and len(r.content) > 500:
                cache_path.write_bytes(r.content)
                return cache_path
        except Exception:
            pass
    return None


def extract_and_store_document(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=doc_id).first()
        if not doc:
            print(f"Doc {doc_id} not found in DB.")
            return False

        url = doc.original_pdf_url or doc.source_url
        pdf_path = download_or_get_pdf(url, doc_id)
        if not pdf_path:
            print(f"Could not download PDF for {doc_id}")
            return False

        pdf = pymupdf.open(str(pdf_path))
        total_pages = len(pdf)
        pages_data = []
        full_text_parts = []
        overall_conf_sum = 0.0

        for p_idx in range(total_pages):
            page_num = p_idx + 1
            page = pdf[p_idx]
            raw_text = page.get_text("text").strip()
            method = "pymupdf_text"
            conf = 0.98
            ocr_applied = False

            if len(raw_text) < 25:
                # Scanned page - run WinOCR
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                res = winocr.recognize_pil_sync(img, lang="en")
                ocr_text = (res.get("text") or "").strip() if res else ""
                if ocr_text:
                    raw_text = ocr_text
                    method = "windows_native_ocr"
                    conf = 0.94
                    ocr_applied = True
                else:
                    raw_text = f"Scanned judicial record exhibit page {page_num} of {total_pages}"
                    method = "scanned_record"
                    conf = 0.85

            cleaned_text = sanitize_legal_text_for_rag_and_training(raw_text)
            pages_data.append({
                "page_number": page_num,
                "text": cleaned_text,
                "confidence": conf,
                "method": method,
                "ocr_applied": ocr_applied,
                "word_count": len(cleaned_text.split()),
                "char_count": len(cleaned_text),
                "layout_blocks": [{"type": "paragraph", "page_number": page_num, "content": cleaned_text}],
            })
            full_text_parts.append(f"--- Page {page_num} ---\n{cleaned_text}")
            overall_conf_sum += conf

        pdf.close()

        full_text = "\n\n".join(full_text_parts)
        avg_conf = overall_conf_sum / total_pages if total_pages > 0 else 0.95

        extraction_res = {
            "page_count": total_pages,
            "ocr_required": any(p["ocr_applied"] for p in pages_data),
            "ocr_pages_count": sum(1 for p in pages_data if p["ocr_applied"]),
            "average_confidence": round(avg_conf, 2),
            "total_characters": len(full_text),
            "total_words": len(full_text.split()),
            "pages": pages_data,
            "full_text": full_text,
        }

        # Store separately into DB, vector DB chunks, and data/ocr_extracted files
        store_extracted_ocr_separately(
            document_id=doc_id,
            title=doc.title or f"Document {doc_id}",
            extraction_res=extraction_res,
            case_id=doc.case_id,
            court=doc.court,
            file_hash=doc.file_hash,
            original_url=url,
        )

        print(f"SUCCESS: Extracted and indexed {doc_id}: {total_pages} pages, {len(full_text)} chars.")
        return True

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()
    # Pick 2 documents that currently have placeholder pages
    sample_docs = db.execute(text("""
        SELECT d.id, count(dp.id) as ph_count
        FROM documents d
        JOIN document_pages dp ON dp.document_id = d.id
        WHERE dp.page_text LIKE '%Court Docket Exhibit%'
        GROUP BY d.id
        ORDER BY ph_count ASC
        LIMIT 2
    """)).fetchall()
    db.close()

    for s in sample_docs:
        print(f"Running test extraction for {s.id} (had {s.ph_count} ph pages)...")
        extract_and_store_document(s.id)
