"""
ALEX v1 — Atomic Legal Extraction Engine
Core package initialization.
"""

from app.alex.ingestion import ingest_and_validate_file
from app.alex.ocr import extract_layout_and_text
from app.alex.classifier import classify_document_alex
from app.alex.extractor import extract_legal_entities
from app.alex.provenance import create_provenance_envelope
from app.alex.atom_builder import build_canonical_atom_25_layers
from app.alex.pipeline import AlexPipeline, run_alex_on_document

__all__ = [
    "ingest_and_validate_file",
    "extract_layout_and_text",
    "classify_document_alex",
    "extract_legal_entities",
    "create_provenance_envelope",
    "build_canonical_atom_25_layers",
    "AlexPipeline",
    "run_alex_on_document",
]
