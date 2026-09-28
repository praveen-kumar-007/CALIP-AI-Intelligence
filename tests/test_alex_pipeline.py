"""
Unit tests for ALEX v1 Extraction Pipeline, Deterministic Legal Rules, and Verification Guardrails.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.alex.ingestion import ingest_and_validate_file
from app.alex.classifier import classify_document_alex
from app.alex.provenance import create_provenance_envelope
from app.alex.atom_builder import calculate_atom_completeness
from app.services.legal_rules import (
    evaluate_cheating_ingredients,
    evaluate_statutory_limitation,
    evaluate_public_servant_sanction,
    evaluate_unexplained_fir_delay,
    run_all_deterministic_rules,
)
from app.services.verification_service import verify_legal_ai_output

client = TestClient(app)


# ==============================================================================
# 1. ALEX EXTRACTION & INGESTION TESTS
# ==============================================================================

def test_alex_ingestion_nonexistent_file():
    res = ingest_and_validate_file("non_existent_file.pdf")
    assert res.is_valid is False
    assert "does not exist" in (res.error_message or "").lower()


def test_alex_classification_taxonomy():
    fir_text = "First Information Report Form 24.5(1) Police Station Shivajinagar U/s 154 Cr.P.C."
    res = classify_document_alex(fir_text, title="FIR 123/2023")
    assert res.document_type == "FIR"
    assert res.confidence >= 0.85
    assert res.taxonomy_category == "POLICE_RECORDS"

    charge_sheet_text = "Final Report under Section 173 Cr.P.C. Doshrop Patra in the Court of Judicial Magistrate"
    res_cs = classify_document_alex(charge_sheet_text)
    assert res_cs.document_type == "CHARGE_SHEET"

    bail_text = "Application under Section 439 Cr.P.C. for grant of Regular Bail"
    res_b = classify_document_alex(bail_text)
    assert res_b.document_type in ("BAIL_APPLICATION", "BAIL_ORDER")


def test_provenance_envelope_schema_compliance():
    env = create_provenance_envelope(
        value="Section 420",
        confidence=0.95,
        document_id="doc_test123",
        page=2,
        quote="Accused committed cheating u/s 420 IPC",
        extraction_method="REGEX",
    )
    assert env["value"] == "Section 420"
    assert env["confidence"] == 0.95
    assert env["source"]["document_id"] == "doc_test123"
    assert env["source"]["page"] == 2
    assert "u/s 420" in env["source"]["quote"]
    assert env["extraction_method"] == "REGEX"
    assert env["verification_status"] == "VERIFIED_ALEX"


# ==============================================================================
# 2. DETERMINISTIC LEGAL RULES TESTS
# ==============================================================================

def test_rule_cheating_ingredients_commercial_dispute():
    """Civil/commercial disputes without inception fraud must flag defense opportunity."""
    res = evaluate_cheating_ingredients(
        sections=["420", "406"],
        allegations=["The petitioner failed to deliver the agreed goods despite receiving advance payment under the MOU."],
        has_contract=True,
    )
    assert res.verdict == "DEFENSE_OPPORTUNITY"
    assert "commercial/civil transaction" in res.summary
    assert any("Uma Shankar Gopalika" in p for p in res.precedents)


def test_rule_cheating_ingredients_fraud_from_inception():
    res = evaluate_cheating_ingredients(
        sections=["420"],
        allegations=["From the inception, the accused presented a counterfeit entity and bogus documents to induce delivery."],
    )
    assert res.verdict == "COMPLIANT"


def test_rule_crpc_468_limitation_exceeded():
    """Section 323 carries 1 yr max; 500 days delay is barred under Section 468 CrPC."""
    res = evaluate_statutory_limitation(
        sections=["323", "341"],
        occurrence_date_str="2022-01-01",
        registration_date_str="2023-08-01",  # ~577 days = ~19 months (> 12 months threshold)
    )
    assert res.verdict == "VIOLATION_FLAGGED"
    assert "Bar of limitation" in res.summary


def test_rule_crpc_468_no_limitation_serious_offense():
    """Section 420 carries 7 yrs max punishment; Section 468 CrPC limitation does NOT bar it."""
    res = evaluate_statutory_limitation(
        sections=["420"],
        occurrence_date_str="2018-01-01",
        registration_date_str="2023-01-01",
    )
    assert res.verdict == "COMPLIANT"
    assert "No statutory limitation bar" in res.summary


def test_rule_public_servant_sanction():
    res = evaluate_public_servant_sanction(
        accused_descriptions=["Police Officer - Sub-Inspector of Police Kotwali"],
        has_sanction_order=False,
    )
    assert res.verdict == "DEFENSE_OPPORTUNITY"
    assert "Section 197" in res.summary


def test_rule_fir_delay():
    res = evaluate_unexplained_fir_delay(
        occurrence_date_str="2023-01-01",
        registration_date_str="2023-03-15",
        delay_explained_in_fir=False,
    )
    assert res.verdict == "DEFENSE_OPPORTUNITY"
    assert "delay" in res.summary.lower()


# ==============================================================================
# 3. VERIFICATION GUARDRAIL TESTS
# ==============================================================================

def test_verification_prohibited_certainty():
    output = "This petition is guaranteed to win before the High Court."
    rep = verify_legal_ai_output(output)
    assert rep.is_grounded is False
    assert any("guaranteed to win" in w for w in rep.guardrail_warnings)


def test_verification_ungrounded_section():
    ground_truth = {"statutory_charges": [{"section": "420"}], "identity_and_coordinates": {"sections": ["420"]}}
    output = "The accused was prosecuted under Section 9999 IPC for an unusual infraction."
    rep = verify_legal_ai_output(output, ground_truth)
    assert rep.is_grounded is False
    assert any("Section 9999" in inc for inc in rep.flagged_inconsistencies)


# ==============================================================================
# 4. REST API ENDPOINTS TESTS
# ==============================================================================

def test_api_review_queue_endpoints():
    res = client.get("/api/review-queue")
    assert res.status_code == 200
    data = res.json()
    assert "pending_count" in data
    assert "items" in data


def test_api_evaluate_legal_rules_endpoint():
    payload = {
        "sections": ["IPC 420"],
        "allegations": ["Contractual delivery agreement between partners"],
        "occurrence_date": "2022-01-01",
        "registration_date": "2023-01-01",
        "has_contract": True,
    }
    res = client.post("/api/rules/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["evaluations_count"] >= 4
