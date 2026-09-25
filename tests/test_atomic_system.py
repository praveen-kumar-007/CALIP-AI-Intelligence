import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.atom_resolver import generate_canonical_fir_id, extract_fir_coordinates, resolve_document_to_atom
from app.services.document_classifier import classify_legal_document
from app.services.hydration_engine import get_all_atoms, get_canonical_atom_json

client = TestClient(app)


def test_canonical_fir_id_generation():
    """Verifies that Canonical FIR IDs strictly follow STATE-DISTRICT-PS-NO-YEAR."""
    fir_id = generate_canonical_fir_id(
        state="Maharashtra",
        district="Pune",
        police_station="Shivajinagar",
        fir_number="123",
        fir_year=2023,
    )
    assert fir_id == "MH-PUNE-SHIVAJINAGAR-0123-2023"

    fir_id_short_year = generate_canonical_fir_id(
        state="MH",
        district="NAGPUR",
        police_station="KOTWALI",
        fir_number="147",
        fir_year="02",
    )
    assert fir_id_short_year == "MH-NAGPUR-KOTWALI-0147-2002"


def test_document_classifier_types():
    """Tests classification of legal statutory documents across various document types."""
    # 1. FIR
    res_fir = classify_legal_document("First Information Report Form No. 24.5(1) U/s 154 Cr.P.C. registered at Police Station")
    assert res_fir["document_type"] == "FIR"
    assert res_fir["confidence"] >= 0.85

    # 2. Charge Sheet
    res_cs = classify_legal_document("Police Report under Section 173 Cr.P.C. Final Report Doshrop Patra in the Court of Magistrate")
    assert res_cs["document_type"] == "CHARGE_SHEET"

    # 3. Bail Application
    res_bail = classify_legal_document("Application for Anticipatory Bail u/s 438 of the Code of Criminal Procedure 1973")
    assert res_bail["document_type"] == "ANTICIPATORY_BAIL"

    # 4. Roznama
    res_roz = classify_legal_document("Daily Order Sheet Roznama of the Court. Next Date of Hearing NDOH fixed for 12/04/2024")
    assert res_roz["document_type"] == "ROZNAMA"

    # 5. Witness Statement
    res_wit = classify_legal_document("Statement under Section 161 Cr.P.C. recorded by Police Inspector Kotwali")
    assert res_wit["document_type"] == "WITNESS_STATEMENT"


def test_atoms_dashboard_html_page():
    """Tests that /atoms server-rendered dashboard loads and contains canonical atoms."""
    response = client.get("/atoms")
    assert response.status_code == 200
    assert "Legal Cognitive Atoms" in response.text
    assert "MH-NAGPUR-KOTWALI-0147-2002" in response.text


def test_atom_detail_html_page():
    """Tests that /atoms/{atom_id} renders the 24 tabs and procedural lineage flow."""
    # Fetch an atom first
    atoms = get_all_atoms(limit=1)
    assert len(atoms) > 0
    atom_id = atoms[0]["id"]

    response = client.get(f"/atoms/{atom_id}")
    assert response.status_code == 200
    assert "Visual Procedural Lineage Flow" in response.text
    assert "Accused &amp; Charges" in response.text
    assert "Grounded Atomic Legal Reasoning Engine" in response.text


def test_api_atoms_list():
    """Tests GET /api/atoms endpoint."""
    response = client.get("/api/atoms?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert "canonical_fir_id" in data["items"][0]


def test_api_atom_detail_json():
    """Tests GET /api/atoms/{atom_id} returns the canonical 25-layer JSON."""
    atoms = get_all_atoms(limit=1)
    atom_id = atoms[0]["id"]

    response = client.get(f"/api/atoms/{atom_id}")
    assert response.status_code == 200
    data = response.json()
    assert "identity" in data
    assert "fir" in data
    assert "case_lineage" in data
    assert "accused" in data
    assert "charges" in data
    assert "hydration_status" in data


def test_api_atom_documents():
    """Tests GET /api/atoms/{atom_id}/documents endpoint."""
    atoms = get_all_atoms(limit=1)
    atom_id = atoms[0]["id"]

    response = client.get(f"/api/atoms/{atom_id}/documents")
    assert response.status_code == 200
    data = response.json()
    assert "canonical_fir_id" in data
    assert "documents" in data


def test_api_atomic_reasoning_endpoint(monkeypatch):
    """Tests POST /api/reason with IRAC grounded reasoning bounded to an atom."""
    from app.services import atomic_reasoner
    monkeypatch.setattr(
        atomic_reasoner,
        "query_llm",
        lambda *args, **kwargs: "Based on the Canonical FIR record, the accused is charged under Section 420."
    )

    atoms = get_all_atoms(limit=1)
    atom_id = atoms[0]["id"]

    payload = {
        "question": "What statutory charges are registered under this FIR matter?",
        "atom_id": atom_id,
    }
    response = client.post("/api/reason", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "atom" in data
    assert "420" in data["answer"]
    assert data["grounded"] is True


def test_review_queue_page_loads():
    """Tests that /admin/review-queue loads for human-in-the-loop verification."""
    response = client.get("/admin/review-queue")
    assert response.status_code == 200
    assert "Atom Verification &amp; Review Queue" in response.text
