from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from sqlalchemy import or_

from app.db.session import SessionLocal
from app.db.models import Case, Document, LongtailFolder, RelationshipEdge, LegalEntity

# Regex patterns for extracting legal identifiers
CASE_NUM_PATTERN = re.compile(
    r"(?:case\s*(?:no\.?|number)?\s*[:\-]?\s*)?(?P<num>\d{1,6}\s*/\s*\d{2,4})",
    re.IGNORECASE,
)
FIR_PATTERN = re.compile(
    r"(?:fir|crime|cr\.?)\s*(?:no\.?|number)?\s*[:\-]?\s*(?P<fir>\d{1,6}\s*/\s*\d{2,4})",
    re.IGNORECASE,
)
COURT_OR_PS_PATTERN = re.compile(
    r"(?P<name>Nagpur|Wardha|Santacruz|EOW|CBI|Sessions\s+Court|High\s+Court|Supreme\s+Court|Special\s+Court)",
    re.IGNORECASE,
)


def extract_case_identifiers(title_or_text: str) -> dict[str, str | None]:
    """
    Extracts structured legal identifiers (case number, FIR number, police station/court, year)
    from titles, filenames, or extracted legal texts.
    """
    cleaned = (title_or_text or "").strip()
    case_num = None
    fir_num = None
    ps_court = None
    year = None

    # FIR extraction
    fir_match = FIR_PATTERN.search(cleaned)
    if fir_match:
        fir_num = re.sub(r"\s+", "", fir_match.group("fir"))
    
    # Generic number extraction (often the FIR or Case number like 147/2002)
    case_match = CASE_NUM_PATTERN.search(cleaned)
    if case_match:
        num_str = re.sub(r"\s+", "", case_match.group("num"))
        if not case_num:
            case_num = num_str
        if not fir_num and ("fir" in cleaned.lower() or "cr" in cleaned.lower()):
            fir_num = num_str

    # Extract PS or Court name
    court_match = COURT_OR_PS_PATTERN.search(cleaned)
    if court_match:
        ps_court = court_match.group("name").strip()

    # Extract year if in format /YYYY or 20YY
    year_match = re.search(r"/(20\d{2}|19\d{2})", cleaned)
    if year_match:
        year = year_match.group(1)

    return {
        "case_number": case_num,
        "fir_number": fir_num,
        "police_station": ps_court,
        "year": year,
    }


def get_case_linkages(case_id: str) -> dict[str, Any]:
    """
    Analyzes a case and returns:
    1. Primary FIR copies (English and Marathi)
    2. Primary Charge Sheet documents & Seizure lists
    3. Connected & companion cases (sharing Police Station, Crime Number, Year, or Subject)
    4. Cross-referenced documents across other cases
    5. Entity relationships from Knowledge Graph
    """
    db = SessionLocal()
    try:
        case = db.query(Case).filter_by(id=case_id).first()
        if not case and not case_id.startswith("lt-"):
            case = db.query(Case).filter_by(id=f"lt-{case_id}").first()
        if not case:
            return {
                "fir_copies": [],
                "charge_sheets": [],
                "connected_cases": [],
                "cross_referenced_documents": [],
                "primary_fir_number": None,
            }

        # Determine primary FIR number
        c_info = extract_case_identifiers(f"{case.title} {case.case_number}")
        primary_fir_num = c_info["fir_number"] or case.case_number

        # 1. Locate FIR Copies within this case
        fir_copies = []
        charge_sheets = []
        
        # Check all documents for this case
        all_case_docs = db.query(Document).filter_by(case_id=case.id).all()
        for doc in all_case_docs:
            doc_lower = (doc.title or "").lower()
            folder_title = doc.folder.title.lower() if doc.folder else ""

            # Check database for text and OCR
            has_txt = bool(doc.extracted_text)
            has_ocr = bool(doc.extracted_text) or bool(doc.pages)

            doc_entry = {
                "id": doc.id,
                "title": doc.title,
                "url": doc.original_pdf_url or doc.source_url,
                "folder_name": doc.folder.title if doc.folder else "Case Files",
                "has_txt": has_txt,
                "has_ocr": has_ocr,
                "document_type": doc.document_type or "Document",
                "file_hash": doc.file_hash,
            }

            # FIR Copies
            if "fir" in doc_lower or "fir" in folder_title:
                is_english = "english" in doc_lower or "english" in folder_title or "eng" in doc_lower
                is_marathi = "marathi" in doc_lower or "marathi" in folder_title
                doc_entry["language"] = "English" if is_english else ("Marathi" if is_marathi else "Original")
                fir_copies.append(doc_entry)

            # Charge Sheets
            elif "charge sheet" in doc_lower or "seizure" in doc_lower or "charge sheet" in folder_title:
                charge_sheets.append(doc_entry)

        # 2. Find Connected / Companion Cases
        connected_cases = []
        # Match cases that share the same police station / jurisdiction or case year
        ps_name = c_info["police_station"]
        if ps_name:
            companion_query = db.query(Case).filter(
                Case.id != case.id,
                (Case.title.ilike(f"%{ps_name}%")) | (Case.court_name.ilike(f"%{ps_name}%")),
            )
            for comp in companion_query.limit(8).all():
                comp_fir = extract_case_identifiers(f"{comp.title} {comp.case_number}")
                connected_cases.append({
                    "id": comp.id,
                    "case_number": comp.case_number,
                    "title": comp.title,
                    "court": comp.court_name,
                    "fir_number": comp_fir["fir_number"] or comp.case_number,
                    "relation_reason": f"Shared Police Station / Jurisdiction ({ps_name})",
                    "doc_count": len(comp.documents),
                })

        # 3. Find Cross-Referenced Documents in Other Cases
        # Look for documents in other cases that mention this case's number or FIR number
        cross_referenced_docs = []
        if case.case_number and len(case.case_number) > 3 and case.case_number != "MIS/SUMMARY":
            pattern_term = f"%{case.case_number}%"
            matched_docs = db.query(Document).filter(
                Document.case_id != case.id,
                or_(
                    Document.title.ilike(pattern_term),
                    Document.extracted_text.ilike(pattern_term),
                )
            ).limit(10).all()

            for md in matched_docs:
                cross_referenced_docs.append({
                    "id": md.id,
                    "title": md.title,
                    "url": md.original_pdf_url or md.source_url,
                    "case_id": md.case_id,
                    "case_title": md.case.title if md.case else "External Case",
                    "has_txt": bool(md.extracted_text),
                    "match_type": "Direct Case / FIR Citation",
                })

        return {
            "primary_fir_number": primary_fir_num,
            "police_station": ps_name,
            "fir_copies": fir_copies,
            "charge_sheets": charge_sheets[:10],
            "connected_cases": connected_cases,
            "cross_referenced_documents": cross_referenced_docs,
        }
    finally:
        db.close()


def get_document_linkages(document_id: str) -> dict[str, Any]:
    """
    Retrieves case linkage, FIR relationship, sibling documents, and cross-references for a document.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            return {}

        case = doc.case
        case_info = None
        fir_info = None
        sibling_docs = []

        if case:
            identifiers = extract_case_identifiers(f"{case.title} {case.case_number}")
            case_info = {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "court": case.court_name,
                "fir_number": identifiers["fir_number"] or case.case_number,
                "police_station": identifiers["police_station"],
            }

            # Sibling documents in the same folder or case
            if doc.folder_id:
                siblings = db.query(Document).filter(
                    Document.folder_id == doc.folder_id,
                    Document.id != doc.id,
                ).limit(8).all()
            else:
                siblings = db.query(Document).filter(
                    Document.case_id == case.id,
                    Document.id != doc.id,
                ).limit(8).all()

            for sib in siblings:
                sibling_docs.append({
                    "id": sib.id,
                    "title": sib.title,
                    "url": sib.original_pdf_url or sib.source_url,
                    "has_txt": bool(sib.extracted_text),
                    "document_type": sib.document_type or "Document",
                })

        # Check if this document itself is an FIR or Charge Sheet
        doc_lower = (doc.title or "").lower()
        is_fir = "fir" in doc_lower
        is_cs = "charge sheet" in doc_lower or "seizure" in doc_lower

        return {
            "document_id": doc.id,
            "case": case_info,
            "is_fir": is_fir,
            "is_charge_sheet": is_cs,
            "sibling_documents": sibling_docs,
        }
    finally:
        db.close()
