"""
ALEX v1 Unified Pipeline Orchestrator.
Coordinates: Ingestion -> Layout/OCR -> Classification -> Entity Extraction -> Atom Linking -> Vector Indexing.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.alex.ingestion import ingest_and_validate_file, IngestionResult
from app.alex.ocr import extract_layout_and_text, DocumentLayout
from app.alex.classifier import classify_document_alex, ClassificationResult
from app.alex.extractor import extract_legal_entities
from app.alex.atom_builder import build_canonical_atom_25_layers
from app.db.session import SessionLocal
from app.db.models import Document, DocumentPage, AtomProvenance
from app.services.atom_resolver import resolve_document_to_atom
from app.services.vector_service import index_document_chunks


@dataclass
class AlexPipelineResult:
    status: str
    document_id: str
    file_hash: str
    classification: dict[str, Any]
    entities_extracted: dict[str, Any]
    atom_id: Optional[str] = None
    canonical_pin: Optional[str] = None
    canonical_atom: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class AlexPipeline:
    def __init__(self):
        pass

    def process_file(
        self,
        file_path: str,
        document_id: Optional[str] = None,
        title: str = "",
        atom_id: Optional[str] = None,
    ) -> AlexPipelineResult:
        """
        Executes the full ALEX v1 pipeline on a single document file.
        """
        # Step 1: Ingestion & Validation
        ingest_res = ingest_and_validate_file(file_path)
        if not ingest_res.is_valid:
            return AlexPipelineResult(
                status="error",
                document_id=document_id or "unknown",
                file_hash=ingest_res.sha256_hash,
                classification={},
                entities_extracted={},
                error=ingest_res.error_message,
            )

        if not document_id:
            document_id = f"doc_{ingest_res.sha256_hash[:16]}"
        if not title:
            title = ingest_res.file_name

        # Step 2: OCR & Layout Preservation
        try:
            layout = extract_layout_and_text(file_path)
        except Exception as e:
            return AlexPipelineResult(
                status="error",
                document_id=document_id,
                file_hash=ingest_res.sha256_hash,
                classification={},
                entities_extracted={},
                error=f"OCR / Layout extraction failed: {str(e)}",
            )

        # Step 3: Classification (22-type taxonomy)
        cls_res = classify_document_alex(
            text=layout.full_text,
            title=title,
        )

        # Step 4: Legal Entity Extraction with Provenance
        entities = extract_legal_entities(
            layout=layout,
            document_id=document_id,
            file_hash=ingest_res.sha256_hash,
            title=title,
        )

        # Step 5: Save/Update in PostgreSQL
        db = SessionLocal()
        resolved_atom_id = atom_id
        resolved_pin = None

        try:
            # Check or create document record
            doc = db.query(Document).filter_by(id=document_id).first()
            if not doc:
                doc = Document(
                    id=document_id,
                    title=title,
                    file_path=file_path,
                    file_hash=ingest_res.sha256_hash,
                    file_size=ingest_res.file_size_bytes,
                    page_count=layout.total_pages,
                    document_type=cls_res.document_type,
                    extracted_text=layout.full_text,
                    status="PUBLISHED",
                )
                db.add(doc)
                db.commit()

                # Add pages
                for p in layout.pages:
                    db.add(
                        DocumentPage(
                            document_id=document_id,
                            page_number=p.page_number,
                            page_text=p.full_text,
                        )
                    )
                db.commit()
            else:
                doc.document_type = cls_res.document_type
                if not doc.extracted_text:
                    doc.extracted_text = layout.full_text
                db.commit()

            # Step 6: Link to Atom
            if not resolved_atom_id:
                link_res = resolve_document_to_atom(
                    document_id=document_id,
                    text=layout.full_text,
                    title=title,
                )
                if link_res.get("atom_id"):
                    resolved_atom_id = link_res["atom_id"]
                    resolved_pin = link_res.get("canonical_fir_id")

            if resolved_atom_id and doc.atom_id != resolved_atom_id:
                doc.atom_id = resolved_atom_id
                db.commit()

            # Save entity provenances to atom_provenance if atom exists
            if resolved_atom_id:
                for sec in entities.get("sections", []):
                    prov = sec.get("provenance", {})
                    src = prov.get("source", {})
                    db.add(
                        AtomProvenance(
                            atom_id=resolved_atom_id,
                            source_document_id=document_id,
                            page_number=src.get("page", 1),
                            verbatim_quote=src.get("quote", "")[:500],
                            target_table="atom_accused_charges",
                            target_field="section",
                        )
                    )
                db.commit()

        finally:
            db.close()

        # Step 7: Index Chunks into Vector DB with atom_id isolation
        try:
            pages_payload = [{"page_number": p.page_number, "text": p.full_text} for p in layout.pages]
            index_document_chunks(
                document_id=document_id,
                case_id=None,
                pages=pages_payload,
                atom_id=resolved_atom_id,
            )
        except Exception as e:
            print(f"[ALEX Pipeline] Vector indexing warning: {e}")

        # Step 8: Hydrate 25-layer Canonical JSON if linked to Atom
        canonical_atom = None
        if resolved_atom_id:
            canonical_atom = build_canonical_atom_25_layers(resolved_atom_id)

        return AlexPipelineResult(
            status="success",
            document_id=document_id,
            file_hash=ingest_res.sha256_hash,
            classification={
                "type": cls_res.document_type,
                "confidence": cls_res.confidence,
                "justification": cls_res.justification,
                "category": cls_res.taxonomy_category,
            },
            entities_extracted=entities,
            atom_id=resolved_atom_id,
            canonical_pin=resolved_pin,
            canonical_atom=canonical_atom,
        )


_default_pipeline = AlexPipeline()


def run_alex_on_document(
    file_path: str,
    document_id: Optional[str] = None,
    title: str = "",
    atom_id: Optional[str] = None,
) -> AlexPipelineResult:
    return _default_pipeline.process_file(file_path, document_id, title, atom_id)
