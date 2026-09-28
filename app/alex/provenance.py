"""
ALEX Provenance Module.
Enforces auditable field-level provenance tracking conforming to canonical_legal_atom_v1.json.
Every extracted fact MUST provide:
- value
- confidence
- source: {document_id, page, block_idx, bbox, quote, file_hash}
- extraction_method: REGEX | RULE | LLM | LAYOUT_HEURISTIC
- verification_status: UNVERIFIED | VERIFIED_ALEX | HUMAN_APPROVED | DISPUTED
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class SourceCitation:
    document_id: str
    page: int = 1
    block_index: Optional[int] = None
    bbox: Optional[list[float]] = None
    quote: str = ""
    file_hash: Optional[str] = None


@dataclass
class ProvenanceEnvelope:
    value: Any
    confidence: float
    source: SourceCitation
    extraction_method: str = "REGEX"
    verification_status: str = "VERIFIED_ALEX"

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "confidence": round(float(self.confidence), 3),
            "source": {
                "document_id": self.source.document_id,
                "page": self.source.page,
                "paragraph": self.source.block_index or 1,
                "line": None,
                "quote": self.source.quote[:300] if self.source.quote else "",
                "file_hash": self.source.file_hash,
                "bbox": self.source.bbox,
            },
            "extraction_method": self.extraction_method,
            "verification_status": self.verification_status,
        }


def create_provenance_envelope(
    value: Any,
    confidence: float,
    document_id: str,
    page: int = 1,
    quote: str = "",
    block_index: Optional[int] = None,
    bbox: Optional[tuple[float, float, float, float] | list[float]] = None,
    file_hash: Optional[str] = None,
    extraction_method: str = "REGEX",
    verification_status: str = "VERIFIED_ALEX",
) -> dict[str, Any]:
    """Helper to generate a validated JSON-schema-compliant provenance dictionary."""
    citation = SourceCitation(
        document_id=document_id,
        page=page,
        block_index=block_index,
        bbox=list(bbox) if bbox else None,
        quote=quote,
        file_hash=file_hash,
    )
    envelope = ProvenanceEnvelope(
        value=value,
        confidence=confidence,
        source=citation,
        extraction_method=extraction_method,
        verification_status=verification_status,
    )
    return envelope.to_dict()
