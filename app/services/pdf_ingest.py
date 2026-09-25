from __future__ import annotations

import hashlib
import os
import re
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests
try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Document, DocumentPage, ProcessingJob
from app.services.ocr_service import extract_text_and_ocr_pdf, store_extracted_ocr_separately
from app.services.graph_service import extract_entities_from_text, save_extracted_entities_and_relationships
from app.services.vector_service import index_document_chunks

DATA_DIR = settings.DATA_DIR
DOWNLOADS_DIR = settings.DOWNLOADS_DIR
INCOMING_DIR = settings.INCOMING_DIR
HEADERS = {"User-Agent": settings.SCRAPER_USER_AGENT}
BASE_URL = settings.LONGTAIL_BASE_URL


def resolve_pdf_links_from_html(html: str, base_url: str = BASE_URL) -> list[dict[str, str]]:
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for tag in soup.select("a[href], iframe[src], object[data], source[src]"):
        href = tag.get("href") or tag.get("src") or tag.get("data")
        if not href:
            continue
        full_url = urljoin(base_url, href)
        lowered = full_url.lower()
        if ".pdf" not in lowered and "/uploads/" not in lowered and "/files/" not in lowered:
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        label = (tag.get_text(" ", strip=True) or Path(unquote(urlparse(full_url).path)).name or "PDF document").strip()
        results.append({"label": label, "url": full_url})
    return results


def extract_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text_parts: list[str] = []
    try:
        for page_number in range(len(doc)):
            page = doc[page_number]
            page_text = page.get_text("text").strip()
            if page_text:
                text_parts.append(page_text)
    finally:
        doc.close()
    return "\n\n".join(text_parts)


def calculate_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_filename(url: str, doc_id: str | None = None) -> str:
    parsed = urlparse(url)
    name = Path(unquote(parsed.path)).name
    if not name or name == ".":
        name = f"doc_{doc_id or 'file'}.pdf"
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    return cleaned[:100]


def download_pdf_file(url: str, doc_id: str | None = None) -> str:
    temp_dir = Path(tempfile.gettempdir()) / "calip_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    file_name = safe_filename(url, doc_id)
    dest_path = temp_dir / file_name

    resp = requests.get(url, headers=HEADERS, timeout=40, stream=True)
    resp.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

    return str(dest_path)


def ingest_local_pdf(
    local_path: str,
    title: str = "Legal Document",
    case_id: str | None = None,
    document_id: str | None = None,
    court: str | None = None,
    document_type: str = "Document",
    original_pdf_url: str | None = None,
) -> dict[str, Any]:
    """
    Ingests any local PDF file (via direct upload, hot-folder drop, or download):
    1. Computes SHA-256 hash & checks duplicates.
    2. Runs advanced multi-stage OCR & layout extraction.
    3. Saves structured records in SQLite (`Document`, `DocumentPage`).
    4. STORES TEXT SEPARATELY in `data/ocr_extracted/`:
       - `{doc_id}.txt` (plain text)
       - `{doc_id}.json` (full layout, block types, word/char counts)
       - `{doc_id}_rag_chunks.json` (semantic chunks with citation metadata)
       - `{doc_id}_llm_context.md` (LLM-ready prompt context)
    5. Extracts legal entities & updates knowledge graph relationships.
    6. Generates semantic vector embeddings & indexes into `DocumentChunk`.
    7. Marks document as PUBLISHED.
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"PDF file does not exist at path: {local_path}")

    file_hash = calculate_sha256(local_path)
    if not document_id:
        document_id = f"doc_{file_hash[:16]}"

    db = SessionLocal()
    job_id = f"job_{document_id}"

    job = db.query(ProcessingJob).filter_by(id=job_id).first()
    if not job:
        job = ProcessingJob(id=job_id, document_id=document_id, stage="EXTRACTING_AND_OCR", status="RUNNING")
        db.add(job)
        db.commit()

    try:
        existing_doc_with_hash = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.id != document_id,
        ).first()

        # 1. Advanced Extraction & OCR
        extraction_res = extract_text_and_ocr_pdf(local_path)
        pages = extraction_res["pages"]
        full_text = extraction_res["full_text"]
        page_count = extraction_res["page_count"]
        ocr_required = extraction_res["ocr_required"]
        avg_confidence = extraction_res["average_confidence"]

        # 2. Store extracted text & RAG artifacts SEPARATELY
        separated_files = store_extracted_ocr_separately(
            document_id=document_id,
            title=title,
            extraction_res=extraction_res,
            case_id=case_id,
            court=court,
            file_hash=file_hash,
            original_url=original_pdf_url,
        )

        # 3. Auto-detect legal metadata from extracted text
        detected_date = None
        date_match = re.search(r"\b(dated?\s*:?\s*)?([0-3]?[0-9][./-][0-1]?[0-9][./-](?:20|19)?[0-9]{2})\b", full_text[:4000], re.IGNORECASE)
        if date_match:
            detected_date = date_match.group(2)

        detected_number = None
        num_match = re.search(r"\b(Crime Register No\.?|FIR No\.?|Outward No:?|C\.?R\.?\s*No\.?|Case No\.?)\s*:?\s*([A-Za-z0-9/_-]+)", full_text[:4000], re.IGNORECASE)
        if num_match:
            detected_number = f"{num_match.group(1).strip()} {num_match.group(2).strip()}"

        detected_type = document_type
        first_chunk = full_text[:3000].upper()
        if detected_type in ("Document", "Legal Document", None):
            if "FIRST INFORMATION REPORT" in first_chunk or "FIR NO" in first_chunk:
                detected_type = "FIR"
            elif "CHARGE SHEET" in first_chunk:
                detected_type = "ChargeSheet"
            elif "JUDGMENT" in first_chunk or "JUDGEMENT" in first_chunk:
                detected_type = "Judgment"
            elif "ORDER" in first_chunk:
                detected_type = "Order"
            elif "CRIME INVESTIGATION" in first_chunk or "INVESTIGATION" in first_chunk or "POLICE" in first_chunk:
                detected_type = "Investigation Report"

        # 4. Create or update Document record
        doc = db.query(Document).filter_by(id=document_id).first()
        extraction_method = "pymupdf_text" if not ocr_required else "advanced_ocr"

        if not doc:
            doc = Document(
                id=document_id,
                case_id=case_id,
                title=title,
                original_pdf_url=original_pdf_url,
                local_pdf_path=None,
                file_hash=file_hash,
                page_count=page_count,
                ocr_required=ocr_required,
                ocr_status="completed",
                ocr_confidence=avg_confidence,
                extraction_method=extraction_method,
                extracted_text=full_text,  # Full text stored directly in PostgreSQL
                processing_status="EXTRACTED",
                court=court,
                document_type=detected_type,
                document_number=detected_number,
                document_date=detected_date,
            )
            db.add(doc)
        else:
            doc.local_pdf_path = None
            doc.file_hash = file_hash
            doc.page_count = page_count
            doc.ocr_required = ocr_required
            doc.ocr_status = "completed"
            doc.ocr_confidence = avg_confidence
            doc.extraction_method = extraction_method
            doc.extracted_text = full_text
            doc.processing_status = "EXTRACTED"
            if detected_type and doc.document_type in ("Document", "Legal Document", None):
                doc.document_type = detected_type
            if detected_number and not doc.document_number:
                doc.document_number = detected_number
            if detected_date and not doc.document_date:
                doc.document_date = detected_date
        db.commit()

        # 4. Save DocumentPages
        db.query(DocumentPage).filter_by(document_id=document_id).delete()
        for p in pages:
            doc_page = DocumentPage(
                id=f"{document_id}_p{p['page_number']}",
                document_id=document_id,
                page_number=p["page_number"],
                page_text=p["text"],
                has_images=p.get("ocr_applied", False),
                ocr_confidence=p["confidence"],
                extraction_method=p["method"],
            )
            db.add(doc_page)
        db.commit()

        # 5. Extract Entities and Graph Edges
        job.stage = "GRAPH_UPDATE"
        db.commit()
        all_entities = []
        for p in pages:
            ents = extract_entities_from_text(p["text"], document_id=document_id, page_number=p["page_number"])
            all_entities.extend(ents)
        save_extracted_entities_and_relationships(case_id, document_id, all_entities)

        # 5b. Automatic Forensic Legal AI Redrafting for Legacy Font or Garbled OCR
        try:
            from app.services.legal_drafter import is_legacy_font_or_garbled, redraft_and_update_document_in_db
            if is_legacy_font_or_garbled(full_text):
                print(f"[PDF Ingest] Detected legacy font / garbled OCR in {document_id}. Triggering AI Legal Redrafter...")
                redraft_and_update_document_in_db(document_id)
                db.refresh(doc)
                full_text = doc.extracted_text or full_text
        except Exception as redraft_err:
            print(f"[PDF Ingest] AI Redraft note: {redraft_err}")

        # 6. Chunking and Vector Embeddings
        job.stage = "EMBEDDING"
        db.commit()
        chunk_count = index_document_chunks(document_id, case_id, pages)

        # 7. Executive Legal Brief / Summary
        try:
            from app.services.summary_service import generate_document_summary
            generate_document_summary(
                document_id=document_id,
                text=full_text,
                title=title,
                court=court,
                document_type=doc.document_type,
                force_regenerate=False,
            )
        except Exception as sum_err:
            print(f"[PDF Ingest] Summary generation note: {sum_err}")

        # 8. Dynamic Atom Resolution & Automatic Hydration
        try:
            from app.services.atom_resolver import resolve_document_to_atom
            from app.services.document_classifier import classify_legal_document
            from app.services.hydration_engine import hydrate_atom_from_db

            # Classify legal document type dynamically
            cls_info = classify_legal_document(text=full_text, title=title)
            doc.document_type = cls_info["document_type"]

            # Resolve to Canonical Legal Cognitive Atom in Supabase PostgreSQL
            res_atom = resolve_document_to_atom(
                document_id=doc.id,
                text=full_text,
                title=title,
                case_context_id=case_id,
            )
            if res_atom.get("atom_id"):
                doc.atom_id = res_atom["atom_id"]
                db.commit()
                # Automatically hydrate the atom with this new OCR copy
                hydrate_atom_from_db(res_atom["atom_id"])
        except Exception as atom_err:
            print(f"[PDF Ingest] Atom resolution warning: {atom_err}")

        # 9. Complete Job
        doc.processing_status = "PUBLISHED"
        job.stage = "PUBLISHED"
        job.status = "SUCCESS"
        job.progress = 100
        db.commit()

        return {
            "document_id": document_id,
            "title": title,
            "file_hash": file_hash,
            "duplicate_of": existing_doc_with_hash.id if existing_doc_with_hash else None,
            "page_count": page_count,
            "ocr_required": ocr_required,
            "average_confidence": avg_confidence,
            "chunks_created": chunk_count,
            "entities_found": len(all_entities),
            "local_path": local_path,
            "separated_storage": separated_files,
            "full_text": full_text,
            "status": "PUBLISHED",
        }
    except Exception as exc:
        job.stage = "FAILED"
        job.status = "ERROR"
        job.error_message = str(exc)
        db.commit()
        raise exc
    finally:
        db.close()


def process_and_ingest_pdf(
    pdf_url: str,
    title: str = "Legal Document",
    case_id: str | None = None,
    document_id: str | None = None,
    court: str | None = None,
    document_type: str = "Document",
    cleanup_temp_pdf: bool = True,
) -> dict[str, Any]:
    """
    Downloads remote PDF from longtailcases / web, extracts OCR and pages,
    stores structured records directly in PostgreSQL (Supabase), and
    cleans up the temporary local PDF file to preserve disk space.
    """
    if not document_id:
        document_id = f"doc_{hashlib.md5(pdf_url.encode()).hexdigest()[:16]}"

    local_path = download_pdf_file(pdf_url, document_id)
    try:
        return ingest_local_pdf(
            local_path=local_path,
            title=title,
            case_id=case_id,
            document_id=document_id,
            court=court,
            document_type=document_type,
            original_pdf_url=pdf_url,
        )
    finally:
        if cleanup_temp_pdf and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass

