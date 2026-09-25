from __future__ import annotations

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

import requests

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Document, DocumentPage
from app.services.ocr_service import (
    OCR_STORAGE_DIR,
    clean_legal_text,
    extract_text_and_ocr_pdf,
    store_extracted_ocr_separately,
)

from app.services.llm_provider import query_llm, get_active_model_name

OLLAMA_GENERATE_URL = settings.OLLAMA_GENERATE_URL
DEFAULT_MODEL = settings.OLLAMA_MODEL or "qwen3:8b"
DOWNLOADS_DIR = settings.DOWNLOADS_DIR


def query_ollama_summary(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 60) -> str | None:
    """
    Invokes production LLM (Groq, NVIDIA NIM, Gemini, or local Ollama)
    for structured legal summarization.
    """
    return query_llm(
        prompt=prompt,
        system_prompt="You are an expert Senior Indian Legal Analyst. Provide structured, authoritative executive legal summaries.",
        temperature=0.2,
        max_tokens=2048,
        timeout=timeout,
    )


def extract_key_legal_entities(text: str) -> dict[str, list[str]]:
    """Heuristic extraction of sections, dates, case numbers, and legal keywords."""
    sections = list(dict.fromkeys(re.findall(
        r"\b(?:Section|Sec\.|u/s|u/sec|under section)\s*([0-9]+[A-Za-z]*(?:\s*,\s*[0-9]+[A-Za-z]*)*(?:\s*(?:IPC|Cr\.?P\.?C\.?|Indian Penal Code|Evidence Act))?)",
        text,
        re.IGNORECASE,
    )))

    dates = list(dict.fromkeys(re.findall(
        r"\b(?:dated?\s*:?\s*)?([0-3]?[0-9][./-][0-1]?[0-9][./-](?:20|19)?[0-9]{2})\b",
        text,
        re.IGNORECASE,
    )))

    fir_or_cr = list(dict.fromkeys(re.findall(
        r"\b(?:Crime Register No\.?|FIR No\.?|Outward No:?|C\.?R\.?\s*No\.?|Case No\.?)\s*:?\s*([A-Za-z0-9/_-]+)",
        text,
        re.IGNORECASE,
    )))

    courts = list(dict.fromkeys(re.findall(
        r"\b(?:HIGH COURT OF [A-Z\s]+|SUPREME COURT OF INDIA|DISTRICT & SESSIONS COURT|MAGISTRATE COURT|POLICE STATION [A-Z\s]+)",
        text,
        re.IGNORECASE,
    )))

    return {
        "sections": sections[:8],
        "dates": dates[:6],
        "case_numbers": fir_or_cr[:4],
        "courts": courts[:4],
    }


def extractive_legal_summary(
    text: str,
    title: str = "Legal Document",
    court: str | None = None,
    document_type: str | None = None,
) -> str:
    """Deterministic, high-fidelity Indian legal summary when Ollama is busy or initializing."""
    cleaned = clean_legal_text(text)
    entities = extract_key_legal_entities(cleaned)
    lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]

    # Select representative paragraphs
    narrative_paragraphs = []
    for line in lines:
        if len(line) > 60 and not line.isupper():
            narrative_paragraphs.append(line)
        if len(narrative_paragraphs) >= 4:
            break

    sec_str = ", ".join(entities["sections"]) if entities["sections"] else "General Criminal / Civil Procedure"
    date_str = ", ".join(entities["dates"][:2]) if entities["dates"] else "Recorded in proceedings"
    case_str = ", ".join(entities["case_numbers"]) if entities["case_numbers"] else "Identified in archive record"
    court_str = court or (entities["courts"][0] if entities["courts"] else "Court of Record / Judicial Forum")

    excerpt = " ".join(narrative_paragraphs[:3])
    if len(excerpt) > 700:
        excerpt = excerpt[:700] + "..."

    summary = (
        f"### 📌 1. DOCUMENT OVERVIEW & NATURE\n"
        f"- **Title**: {title}\n"
        f"- **Document Type**: {document_type or 'Legal Filing / Court Record'}\n"
        f"- **Court / Authority**: {court_str}\n"
        f"- **Reference / Filing Date**: {date_str}\n"
        f"- **Case / FIR Reference**: {case_str}\n\n"
        f"### 👥 2. PARTIES & JURISDICTION\n"
        f"- **Forum / Police Station**: {court_str}\n"
        f"- **Identified Matters**: State / Informant vs. Accused / Respondents as detailed in record\n\n"
        f"### ⚖️ 3. CORE STATUTORY PROVISIONS & CHARGES\n"
        f"- **Invoked Sections**: {sec_str}\n"
        f"- **Operative Matter**: Examination of legal proceedings, investigation filings, and record evidence.\n\n"
        f"### 📜 4. SUMMARY OF RECORD & EVIDENCE\n"
        f"{excerpt or 'Record contains comprehensive verified court proceedings, police filings, and judicial records.'}\n\n"
        f"### 💡 5. KEY TAKEAWAYS FOR COUNSEL\n"
        f"- Verified digital preservation with cryptographic SHA-256 integrity.\n"
        f"- Key statutory references: `{sec_str}`.\n"
        f"- Consult verified source pages for exact evidentiary depositions and cross-examinations."
    )
    return summary


_SUMMARY_MEMORY_CACHE: dict[str, dict[str, Any]] = {}


def generate_document_summary(
    document_id: str,
    text: str,
    title: str = "Legal Document",
    court: str | None = None,
    document_type: str | None = None,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    """
    Generates a structured executive legal summary using local Ollama model (qwen3:8b)
    with automatic persistent caching and rule-based fallback.
    """
    if not force_regenerate and document_id in _SUMMARY_MEMORY_CACHE:
        return _SUMMARY_MEMORY_CACHE[document_id]

    summary_json_path = OCR_STORAGE_DIR / f"{document_id}_summary.json"
    if not force_regenerate and summary_json_path.exists():
        try:
            cached = json.loads(summary_json_path.read_text(encoding="utf-8"))
            if cached.get("summary_text") and len(cached["summary_text"]) > 100:
                _SUMMARY_MEMORY_CACHE[document_id] = cached
                return cached
        except Exception:
            pass

    cleaned_text = clean_legal_text(text)
    if not cleaned_text or len(cleaned_text) < 30:
        cleaned_text = f"Legal record: {title}. Court: {court or 'Competent Jurisdiction'}. Type: {document_type or 'Document'}."

    # Sample text for prompt: up to 4500 chars (first 3000 + last 1500)
    if len(cleaned_text) > 4500:
        prompt_text = cleaned_text[:3000] + "\n\n[... intermediate pages ...]\n\n" + cleaned_text[-1500:]
    else:
        prompt_text = cleaned_text

    prompt = f"""You are an expert Senior Indian Legal Analyst.
Analyze the following extracted legal text from document ID "{document_id}" with Title: "{title}".
Court/Forum: "{court or 'Judicial Forum'}".
Document Type: "{document_type or 'Legal Filing'}".

Provide a structured, professional Executive Legal Summary in Markdown format with these exact 5 sections:
### 📌 1. DOCUMENT OVERVIEW & NATURE
(Specify exact document type, court/forum, dates, and Case/FIR numbers mentioned)

### 👥 2. PARTIES & JURISDICTION
(Identify Petitioner/Informant, Respondent/Accused, and Police Station/Jurisdiction)

### ⚖️ 3. CORE ALLEGATIONS & LEGAL ISSUES
(Detail the facts, dispute, and statutory sections invoked e.g. IPC, CrPC, Evidence Act)

### 📜 4. KEY ORDERS, FINDINGS & RELIEF
(Operative directions, bail/custody status, interim relief, or court observations)

### 💡 5. KEY TAKEAWAYS FOR COUNSEL
(Critical evidentiary aspects, timelines, compliance instructions, and next steps)

Extracted Legal Text:
\"\"\"
{prompt_text}
\"\"\"

Be precise, objective, quote exact Section numbers and dates where present, and format clearly with bullet points.
"""

    ai_response = query_ollama_summary(prompt=prompt, model=DEFAULT_MODEL, timeout=90)
    source_model = get_active_model_name() if ai_response else "deterministic_legal_engine"
    final_summary = ai_response if ai_response else extractive_legal_summary(
        cleaned_text, title=title, court=court, document_type=document_type
    )

    result_data = {
        "document_id": document_id,
        "title": title,
        "court": court,
        "document_type": document_type,
        "model": source_model,
        "summary_text": final_summary,
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "char_count": len(final_summary),
        "source_chars_analyzed": len(cleaned_text),
    }

    _SUMMARY_MEMORY_CACHE[document_id] = result_data

    if os.getenv("SAVE_LOCAL_OCR_FILES", "false").lower() == "true":
        try:
            summary_md_path = OCR_STORAGE_DIR / f"{document_id}_summary.md"
            summary_md_path.write_text(final_summary, encoding="utf-8")
            summary_json_path.write_text(json.dumps(result_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[SummaryService] Error caching summary to disk: {e}")

    return result_data


def get_document_summary(document_id: str) -> dict[str, Any] | None:
    """Loads cached summary from memory or disk if available."""
    if document_id in _SUMMARY_MEMORY_CACHE:
        return _SUMMARY_MEMORY_CACHE[document_id]

    summary_json_path = OCR_STORAGE_DIR / f"{document_id}_summary.json"
    if summary_json_path.exists():
        try:
            cached = json.loads(summary_json_path.read_text(encoding="utf-8"))
            _SUMMARY_MEMORY_CACHE[document_id] = cached
            return cached
        except Exception:
            pass
    return None


def find_local_pdf_for_document(doc_id: str, original_url: str | None = None, title: str | None = None) -> Path | None:
    """Finds matching PDF in data/downloads/ or data/incoming/."""
    candidates = []
    if DOWNLOADS_DIR.exists():
        candidates.extend(list(DOWNLOADS_DIR.glob("*.pdf")))
    if settings.INCOMING_DIR.exists():
        candidates.extend(list(settings.INCOMING_DIR.glob("*.pdf")))
    
    # Check original_url filename
    if original_url:
        url_name = Path(original_url).name
        for p in candidates:
            if p.name.lower() == url_name.lower():
                return p

    # Check doc_id stem
    for p in candidates:
        clean_stem = p.stem.replace("-", "_").replace(".", "_")
        clean_doc = doc_id.replace("doc-", "").replace("doc_", "").replace("-", "_").replace(".", "_")
        if clean_doc in clean_stem or clean_stem in clean_doc:
            return p

    # Check title match
    if title:
        sanitized = re.sub(r"[^A-Za-z0-9]", "", title).lower()
        if len(sanitized) > 4:
            for p in candidates:
                p_clean = re.sub(r"[^A-Za-z0-9]", "", p.stem).lower()
                if sanitized in p_clean or p_clean in sanitized:
                    return p

    return None


def batch_extract_and_summarize_all(limit: int | None = None, summarize: bool = True) -> dict[str, Any]:
    """
    Scans data/downloads/ and data/calip.db:
    1. Ingests and extracts all un-extracted PDFs using PyMuPDF / Windows OCR.
    2. Ensures separated TXT, JSON, RAG chunks are written to data/ocr_extracted/.
    3. Runs AI Legal Summary for each document.
    4. Auto-heals existing DB documents with missing separated files.
    5. Updates database records.
    """
    db = SessionLocal()
    processed_count = 0
    summarized_count = 0
    errors: list[str] = []

    try:
        # Step A: Scan all local downloaded PDFs
        pdf_files = list(DOWNLOADS_DIR.glob("*.pdf")) if DOWNLOADS_DIR.exists() else []
        pdf_files.sort(key=lambda x: x.stat().st_size)

        if limit:
            pdf_files = pdf_files[:limit]

        for pdf_path in pdf_files:
            try:
                filename = pdf_path.name
                doc = db.query(Document).filter(
                    (Document.original_pdf_url.like(f"%{filename}%"))
                    | (Document.local_pdf_path.like(f"%{filename}%"))
                    | (Document.id.like(f"%{pdf_path.stem.replace('-', '_')}%"))
                ).first()

                doc_id = doc.id if doc else f"doc_{pdf_path.stem.replace('-', '_')}"

                full_text = ""
                if doc and doc.extracted_text and len(doc.extracted_text) > 10:
                    full_text = doc.extracted_text
                else:
                    # Ingest or re-ingest local PDF to guarantee all DB records
                    from app.services.pdf_ingest import ingest_local_pdf
                    title = doc.title if doc else pdf_path.stem.replace("_", " ").replace("-", " ")
                    res = ingest_local_pdf(
                        local_path=str(pdf_path),
                        title=title,
                        document_id=doc_id,
                        case_id=doc.case_id if doc else None,
                        court=doc.court if doc else None,
                        original_pdf_url=doc.original_pdf_url if doc else None,
                    )
                    full_text = res.get("full_text", "")
                    processed_count += 1

                if summarize and full_text:
                    doc_title = doc.title if doc else pdf_path.stem
                    doc_court = doc.court if doc else None
                    doc_type = doc.document_type if doc else "Legal Document"
                    generate_document_summary(
                        document_id=doc_id,
                        text=full_text,
                        title=doc_title,
                        court=doc_court,
                        document_type=doc_type,
                        force_regenerate=False,
                    )
                    summarized_count += 1

            except Exception as e:
                errors.append(f"{pdf_path.name}: {str(e)}")

        # Step B: Summarize any existing DB documents that have text
        if summarize:
            existing_docs = db.query(Document).filter(Document.extracted_text.isnot(None)).all()
            for ed in existing_docs:
                sum_file = OCR_STORAGE_DIR / f"{ed.id}_summary.json"
                if not sum_file.exists() and ed.extracted_text:
                    generate_document_summary(
                        document_id=ed.id,
                        text=ed.extracted_text,
                        title=ed.title or "Legal Document",
                        court=ed.court,
                        document_type=ed.document_type,
                        force_regenerate=False,
                    )
                    summarized_count += 1

    finally:
        db.close()

    return {
        "total_pdfs_scanned": len(pdf_files),
        "processed_count": processed_count,
        "summarized_count": summarized_count,
        "errors": errors,
    }
