"""
ALEX Document Classifier Module.
Classifies legal documents into the authoritative 22-type Indian criminal taxonomy
with confidence scores and explicit textual justification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.document_classifier import (
    classify_legal_document,
    CLASSIFICATION_RULES,
)

DOCUMENT_TAXONOMY = {
    "POLICE_RECORDS": [
        "FIR",
        "COMPLAINT",
        "SUPPLEMENTARY_CHARGE_SHEET",
        "CHARGE_SHEET",
        "CLOSURE_REPORT",
    ],
    "INVESTIGATION_RECORDS": [
        "PANCHNAMA",
        "SEIZURE_MEMO",
        "REMAND_APPLICATION",
        "CONFESSION_164",
        "WITNESS_STATEMENT",
        "INQUEST_REPORT",
    ],
    "FORENSIC_MEDICAL": [
        "MEDICAL_LEGAL_CERTIFICATE",
        "FORENSIC_REPORT",
        "DIGITAL_65B_CERTIFICATE",
    ],
    "BAIL_AND_LIBERTY": [
        "BAIL_APPLICATION",
        "BAIL_ORDER",
        "ANTICIPATORY_BAIL",
    ],
    "TRIAL_AND_COURT_PROCEEDINGS": [
        "ROZNAMA",
        "ORDER_SHEET",
        "SECTION_313_STATEMENT",
        "SANCTION_ORDER",
        "TRIAL_JUDGMENT",
    ],
    "APPELLATE_AND_SUPERVISORY": [
        "HIGH_COURT_ORDER",
        "SUPREME_COURT_ORDER",
        "QUASHING_PETITION",
        "PRECEDENT",
    ],
    "MISCELLANEOUS": [
        "OTHER",
        "LEGAL_DOCUMENT",
    ],
}


@dataclass
class ClassificationResult:
    document_type: str
    confidence: float
    justification: str
    taxonomy_category: str
    method: str = "taxonomic_pattern_ensemble"


def classify_document_alex(
    text: str,
    title: str = "",
    folder_context: str = "",
) -> ClassificationResult:
    """
    Classifies a legal document into one of the standard types:
    FIR, CHARGE_SHEET, SUPPLEMENTARY_CHARGE_SHEET, CLOSURE_REPORT,
    PANCHNAMA, SEIZURE_MEMO, REMAND_APPLICATION, BAIL_APPLICATION,
    BAIL_ORDER, ANTICIPATORY_BAIL, WITNESS_STATEMENT, CONFESSION_164,
    MEDICAL_LEGAL_CERTIFICATE, FORENSIC_REPORT, INQUEST_REPORT,
    SANCTION_ORDER, ROZNAMA, SECTION_313_STATEMENT, ORDER_SHEET,
    TRIAL_JUDGMENT, HIGH_COURT_ORDER, SUPREME_COURT_ORDER, OTHER.
    """
    res = classify_legal_document(text=text, title=title, folder_context=folder_context)
    doc_type = res.get("document_type", "OTHER")
    conf = float(res.get("confidence", 0.50))

    # Determine taxonomy category
    category = "MISCELLANEOUS"
    for cat_name, types in DOCUMENT_TAXONOMY.items():
        if doc_type in types:
            category = cat_name
            break

    justification = f"Classified as {doc_type} based on structural markers, keywords and layout patterns."

    return ClassificationResult(
        document_type=doc_type,
        confidence=conf,
        justification=justification,
        taxonomy_category=category,
        method=res.get("classification_method", "taxonomic_pattern_ensemble"),
    )
