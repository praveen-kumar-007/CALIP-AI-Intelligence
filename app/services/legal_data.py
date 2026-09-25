from __future__ import annotations

from typing import Any
from app.db.session import SessionLocal
from app.db.models import Case, Document, Judgment, Order, Application, Court, Act, Section, LongtailFolder
from app.services.longtail_scraper import get_cached_or_live_catalog, sync_catalog_to_database


_SEED_CHECKED = False

def ensure_seed_data():
    """Initializes database with longtail cases catalog if cases table is empty."""
    global _SEED_CHECKED
    if _SEED_CHECKED:
        return
    db = SessionLocal()
    try:
        case_count = db.query(Case).count()
        if case_count > 0:
            _SEED_CHECKED = True
            return
        if case_count == 0:
            print("[LegalData] DB is empty. Loading longtailcases catalog...")
            catalog = get_cached_or_live_catalog()
            sync_catalog_to_database(catalog)
            print("[LegalData] Catalog synced successfully.")
    except Exception as exc:
        print(f"[LegalData] Seed warning: {exc}")
    finally:
        db.close()


def get_all_cases(limit: int = 50, offset: int = 0, state: str | None = None, query: str | None = None) -> list[dict[str, Any]]:
    ensure_seed_data()
    db = SessionLocal()
    try:
        q = db.query(Case)
        if state:
            q = q.filter(Case.subject.ilike(f"%{state}%"))
        if query:
            q = q.filter(
                (Case.title.ilike(f"%{query}%"))
                | (Case.case_number.ilike(f"%{query}%"))
                | (Case.court_name.ilike(f"%{query}%"))
            )
        cases = q.offset(offset).limit(limit).all()
        return [
            {
                "id": c.id,
                "case_number": c.case_number,
                "title": c.title,
                "court": c.court_name,
                "bench": c.bench,
                "status": c.status,
                "case_type": c.case_type,
                "case_year": c.case_year,
                "filing_date": c.filing_date,
                "summary": c.summary,
                "subject": c.subject,
                "source_url": c.source_url,
                "canonical_url": f"/cases/{c.id}",
                "doc_count": len(c.documents),
            }
            for c in cases
        ]
    finally:
        db.close()


def get_case_by_id(case_id: str) -> dict[str, Any] | None:
    ensure_seed_data()
    db = SessionLocal()
    try:
        c = db.query(Case).filter_by(id=case_id).first()
        if not c:
            # Also try matching lt-{case_id}
            c = db.query(Case).filter_by(id=f"lt-{case_id}").first()
        if not c:
            return None

        from app.services.linkage_service import get_case_linkages

        # Build folder hierarchy for case
        folders = db.query(LongtailFolder).filter_by(case_id=c.id, parent_id=None).all()
        folder_tree = []
        for f in folders:
            subfolders = db.query(LongtailFolder).filter_by(parent_id=f.id).all()
            f_docs = []
            for d in f.documents:
                has_txt = bool(d.extracted_text)
                has_ocr = bool(d.extracted_text) or bool(d.pages)
                f_docs.append({
                    "id": d.id,
                    "title": d.title,
                    "url": d.original_pdf_url or d.source_url,
                    "has_txt": has_txt,
                    "has_ocr": has_ocr,
                    "document_type": d.document_type or "Document",
                })

            sub_tree = []
            for sf in subfolders:
                sf_docs = []
                for d in sf.documents:
                    has_txt = bool(d.extracted_text)
                    has_ocr = bool(d.extracted_text) or bool(d.pages)
                    sf_docs.append({
                        "id": d.id,
                        "title": d.title,
                        "url": d.original_pdf_url or d.source_url,
                        "has_txt": has_txt,
                        "has_ocr": has_ocr,
                        "document_type": d.document_type or "Document",
                    })
                sub_tree.append({
                    "id": sf.id,
                    "title": sf.title,
                    "documents": sf_docs,
                })
            folder_tree.append({
                "id": f.id,
                "title": f.title,
                "documents": f_docs,
                "subfolders": sub_tree,
            })

        # Calculate rich case linkages (FIR copies, charge sheets, connected cases)
        linkages = get_case_linkages(c.id)

        case_docs = []
        for d in c.documents:
            has_txt = bool(d.extracted_text)
            has_ocr = bool(d.extracted_text) or bool(d.pages)
            case_docs.append({
                "id": d.id,
                "title": d.title,
                "document_type": d.document_type or "Document",
                "url": d.original_pdf_url or d.source_url,
                "page_count": d.page_count,
                "ocr_status": d.ocr_status,
                "has_txt": has_txt,
                "has_ocr": has_ocr,
            })

        return {
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "court": c.court_name,
            "bench": c.bench,
            "status": c.status,
            "case_type": c.case_type,
            "case_year": c.case_year,
            "filing_date": c.filing_date,
            "summary": c.summary,
            "subject": c.subject,
            "source_url": c.source_url,
            "canonical_url": f"/cases/{c.id}",
            "documents": case_docs,
            "folder_tree": folder_tree,
            "linkages": linkages,
        }
    finally:
        db.close()


def get_all_documents(limit: int = 50, offset: int = 0, query: str | None = None) -> list[dict[str, Any]]:
    ensure_seed_data()
    db = SessionLocal()
    try:
        q = db.query(Document)
        if query:
            q = q.filter(
                (Document.title.ilike(f"%{query}%"))
                | (Document.court.ilike(f"%{query}%"))
            )
        docs = q.offset(offset).limit(limit).all()
        result = []
        for d in docs:
            has_txt = bool(d.extracted_text)
            has_ocr = bool(d.extracted_text) or bool(d.pages)
            result.append({
                "id": d.id,
                "case_id": d.case_id,
                "case_number": d.case.case_number if d.case else None,
                "case_title": d.case.title if d.case else None,
                "title": d.title,
                "document_type": d.document_type or "Document",
                "court": d.court,
                "document_date": d.document_date,
                "source_url": d.source_url,
                "pdf_url": d.original_pdf_url,
                "page_count": d.page_count,
                "file_hash": d.file_hash,
                "ocr_status": d.ocr_status,
                "ocr_confidence": d.ocr_confidence,
                "processing_status": d.processing_status,
                "has_txt": has_txt,
                "has_ocr": has_ocr,
            })
        return result
    finally:
        db.close()


def get_document_by_id(document_id: str) -> dict[str, Any] | None:
    ensure_seed_data()
    db = SessionLocal()
    try:
        from app.services.linkage_service import get_document_linkages
        d = db.query(Document).filter_by(id=document_id).first()
        if not d:
            return None
        
        has_txt = bool(d.extracted_text)
        has_ocr = bool(d.extracted_text) or bool(d.pages)
        linkages = get_document_linkages(d.id)

        return {
            "id": d.id,
            "case_id": d.case_id,
            "title": d.title,
            "document_type": d.document_type,
            "court": d.court,
            "document_date": d.document_date,
            "source_url": d.source_url,
            "pdf_url": d.original_pdf_url,
            "page_count": d.page_count,
            "file_hash": d.file_hash,
            "ocr_status": d.ocr_status,
            "ocr_confidence": d.ocr_confidence,
            "extraction_method": d.extraction_method,
            "extracted_text": d.extracted_text,
            "original_language_text": d.original_language_text,
            "english_translated_text": d.english_translated_text,
            "detected_language": d.detected_language or "English",
            "processing_status": d.processing_status,
            "has_txt": has_txt,
            "has_ocr": has_ocr,
            "linkages": linkages,
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.page_text,
                    "page_text": p.page_text,
                    "original_page_text": p.original_page_text or p.page_text,
                    "english_page_text": p.english_page_text or p.page_text,
                    "confidence": p.ocr_confidence or 0.95,
                    "ocr_confidence": p.ocr_confidence or 0.95,
                    "method": p.extraction_method or "pymupdf_text",
                    "extraction_method": p.extraction_method or "pymupdf_text",
                }
                for p in d.pages
            ],
        }
    finally:
        db.close()


def get_all_judgments(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        judgments = db.query(Judgment).offset(offset).limit(limit).all()
        results = [
            {
                "id": j.id,
                "case_id": j.case_id,
                "title": j.title,
                "date": j.date,
                "court": j.court,
                "bench": j.bench,
                "summary": j.summary,
                "document_id": j.document_id,
            }
            for j in judgments
        ]
        # Also query documents categorized as judgments from the database
        if len(results) < limit:
            docs = (
                db.query(Document)
                .filter(
                    (Document.document_type.ilike("%judgment%"))
                    | (Document.title.ilike("%judgment%"))
                )
                .offset(offset)
                .limit(limit - len(results))
                .all()
            )
            for d in docs:
                results.append({
                    "id": d.id,
                    "case_id": d.case_id,
                    "title": d.title,
                    "date": d.document_date or (d.created_at.strftime("%Y-%m-%d") if d.created_at else None),
                    "court": d.court or "Court of Record",
                    "bench": None,
                    "summary": (d.extracted_text[:200] + "...") if d.extracted_text else f"{d.title} ({d.document_type})",
                    "document_id": d.id,
                })
        return results
    finally:
        db.close()


def get_judgment_by_id(judgment_id: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        j = db.query(Judgment).filter_by(id=judgment_id).first()
        if j:
            return {
                "id": j.id,
                "case_id": j.case_id,
                "title": j.title,
                "date": j.date,
                "court": j.court,
                "bench": j.bench,
                "judges": j.judges,
                "summary": j.summary,
                "issues": j.issues,
                "reasoning": j.reasoning,
                "decision": j.decision,
                "document_id": j.document_id,
            }
        d = db.query(Document).filter_by(id=judgment_id).first()
        if d:
            return {
                "id": d.id,
                "case_id": d.case_id,
                "title": d.title,
                "date": d.document_date or (d.created_at.strftime("%Y-%m-%d") if d.created_at else None),
                "court": d.court or "Court of Record",
                "bench": None,
                "judges": None,
                "summary": d.extracted_text[:400] if d.extracted_text else d.title,
                "issues": None,
                "reasoning": None,
                "decision": None,
                "document_id": d.id,
            }
        return None
    finally:
        db.close()


def get_all_orders(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        orders = db.query(Order).offset(offset).limit(limit).all()
        results = [
            {
                "id": o.id,
                "case_id": o.case_id,
                "order_date": o.order_date,
                "court": o.court,
                "bench": o.bench,
                "order_type": o.order_type,
                "summary": o.summary,
                "document_id": o.document_id,
            }
            for o in orders
        ]
        # Also query documents categorized as orders from the database
        if len(results) < limit:
            order_docs = (
                db.query(Document)
                .filter(
                    (Document.document_type.in_(["Order", "Application / Order"]))
                    | (Document.title.ilike("%order%"))
                )
                .offset(offset)
                .limit(limit - len(results))
                .all()
            )
            for d in order_docs:
                results.append({
                    "id": d.id,
                    "case_id": d.case_id,
                    "order_date": d.document_date or (d.created_at.strftime("%Y-%m-%d") if d.created_at else None),
                    "court": d.court or "Court of Record",
                    "bench": None,
                    "order_type": d.document_type or "Order",
                    "summary": (d.extracted_text[:200] + "...") if d.extracted_text else f"{d.title} ({d.document_type})",
                    "document_id": d.id,
                })
        return results
    finally:
        db.close()


def get_order_by_id(order_id: str) -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        o = db.query(Order).filter_by(id=order_id).first()
        if o:
            return {
                "id": o.id,
                "case_id": o.case_id,
                "order_date": o.order_date,
                "court": o.court,
                "bench": o.bench,
                "order_type": o.order_type,
                "summary": o.summary,
                "directions": o.directions,
                "document_id": o.document_id,
            }
        d = db.query(Document).filter_by(id=order_id).first()
        if d:
            return {
                "id": d.id,
                "case_id": d.case_id,
                "order_date": d.document_date or (d.created_at.strftime("%Y-%m-%d") if d.created_at else None),
                "court": d.court or "Court of Record",
                "bench": None,
                "order_type": d.document_type or "Order",
                "summary": d.extracted_text[:400] if d.extracted_text else d.title,
                "directions": None,
                "document_id": d.id,
            }
        return None
    finally:
        db.close()


def get_all_courts() -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        courts = db.query(Court).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "court_type": c.court_type,
                "jurisdiction": c.jurisdiction,
                "state": c.state,
                "case_count": len(c.cases),
            }
            for c in courts
        ]
    finally:
        db.close()


def get_platform_statistics() -> dict[str, Any]:
    db = SessionLocal()
    try:
        from app.db.models import DocumentChunk, LegalEntity, DocumentPage
        return {
            "cases_count": db.query(Case).count(),
            "documents_count": db.query(Document).count(),
            "courts_count": db.query(Court).count(),
            "folders_count": db.query(LongtailFolder).count(),
            "chunks_count": db.query(DocumentChunk).count(),
            "entities_count": db.query(LegalEntity).count(),
            "ocr_documents_count": db.query(Document).filter(Document.extracted_text.isnot(None), Document.extracted_text != "").count(),
            "pages_count": db.query(DocumentPage).count(),
        }
    finally:
        db.close()


def get_jurisdiction_summary() -> list[dict[str, Any]]:
    """Returns dynamic jurisdiction and subject breakdown directly from the cases table in DB."""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        rows = (
            db.query(Case.subject, func.count(Case.id))
            .filter(Case.subject.isnot(None))
            .group_by(Case.subject)
            .order_by(func.count(Case.id).desc())
            .all()
        )
        return [{"subject": r[0], "count": r[1]} for r in rows if r[0]]
    finally:
        db.close()

