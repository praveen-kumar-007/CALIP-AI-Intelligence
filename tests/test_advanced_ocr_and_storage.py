import json
from pathlib import Path
import fitz
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ocr_service import (
    clean_legal_text,
    detect_layout_blocks,
    deskew_image,
    preprocess_image_for_ocr,
    store_extracted_ocr_separately,
    get_extracted_ocr_data,
    get_llm_ready_context,
    OCR_STORAGE_DIR,
)
from app.services.pdf_ingest import ingest_local_pdf, INCOMING_DIR, DOWNLOADS_DIR
from app.services.auto_sync import scan_and_ingest_incoming_folder

client = TestClient(app)


def test_clean_legal_text():
    raw = "The peti-\ntioner filed an appli-\ncation under Sec.  406 IPC.\r\n\r\n\r\n\r\nOrder passed."
    cleaned = clean_legal_text(raw)
    assert "petitioner" in cleaned
    assert "application" in cleaned
    assert "Sec. 406 IPC." in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned


def test_detect_layout_blocks():
    text = (
        "IN THE HIGH COURT OF JUDICATURE AT BOMBAY\n"
        "CRIMINAL REVISION APPLICATION NO. 147 OF 2002\n"
        "State of Maharashtra versus Accused Person.\n"
        "Section 406 and Section 420 of Indian Penal Code apply.\n"
        "The applicant was heard at length on the merits of the order."
    )
    blocks = detect_layout_blocks(text, page_number=1)
    assert len(blocks) >= 2
    types = [b["type"] for b in blocks]
    assert "header" in types or "citation" in types
    assert "paragraph" in types


def test_deskew_image():
    # Create synthetic test image
    img = np.zeros((100, 100), dtype=np.uint8)
    # Add synthetic diagonal line
    img[40:60, 40:60] = 255
    res = deskew_image(img)
    assert res is not None
    assert res.shape == (100, 100)


def test_store_extracted_ocr_separately(tmp_path):
    doc_id = "test_doc_separate_999"
    title = "Test Judgment on Bail"
    fake_extraction = {
        "page_count": 2,
        "ocr_required": True,
        "ocr_pages_count": 1,
        "average_confidence": 0.94,
        "total_characters": 180,
        "total_words": 28,
        "pages": [
            {
                "page_number": 1,
                "text": "ORDER\nThe applicant is admitted to bail on furnishing PR bond.",
                "confidence": 0.95,
                "method": "advanced_ocr",
                "layout_blocks": [
                    {"type": "header", "content": "ORDER", "char_count": 5, "page_number": 1},
                    {"type": "paragraph", "content": "The applicant is admitted to bail on furnishing PR bond.", "char_count": 56, "page_number": 1},
                ],
            },
            {
                "page_number": 2,
                "text": "Certified copy to be issued forthwith.",
                "confidence": 0.93,
                "method": "advanced_ocr",
                "layout_blocks": [
                    {"type": "paragraph", "content": "Certified copy to be issued forthwith.", "char_count": 38, "page_number": 2},
                ],
            },
        ],
        "full_text": "ORDER\nThe applicant is admitted to bail on furnishing PR bond.\n\nCertified copy to be issued forthwith.",
    }

    paths = store_extracted_ocr_separately(
        document_id=doc_id,
        title=title,
        extraction_res=fake_extraction,
        case_id="case_147_2002",
        court="High Court Bombay",
        file_hash="abc123hash",
    )

    # Check files created
    assert Path(paths["plain_text"]).exists()
    assert Path(paths["structured_json"]).exists()
    assert Path(paths["rag_chunks_json"]).exists()
    assert Path(paths["llm_context_md"]).exists()

    # Verify plain text content
    txt_content = Path(paths["plain_text"]).read_text(encoding="utf-8")
    assert "admitted to bail" in txt_content

    # Verify structured JSON
    data = get_extracted_ocr_data(doc_id)
    assert data is not None
    assert data["document_id"] == doc_id
    assert data["court"] == "High Court Bombay"
    assert len(data["pages"]) == 2

    # Verify LLM Context content
    llm_ctx = get_llm_ready_context(doc_id)
    assert llm_ctx is not None
    assert "[[PAGE 1 | SOURCE: Test Judgment on Bail" in llm_ctx
    assert "--- START VERIFIED DOCUMENT TEXT ---" in llm_ctx


def test_ingest_local_pdf_and_api_endpoints(tmp_path):
    # 1. Create a synthetic PDF document
    pdf_path = tmp_path / "high_court_order.pdf"
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((72, 72), "IN THE HIGH COURT OF JUDICATURE AT BOMBAY\nCRIMINAL REVISION APPLICATION NO. 147 OF 2002\nBefore Hon'ble Single Judge.")
    p1.insert_text((72, 120), "Order: Section 406 IPC charge framed. Matter posted for regular hearing.")
    doc.save(str(pdf_path))
    doc.close()

    # 2. Ingest local PDF
    ingest_res = ingest_local_pdf(
        local_path=str(pdf_path),
        title="High Court Revision Order 147/2002",
        court="Bombay High Court",
        document_type="Order",
    )

    doc_id = ingest_res["document_id"]
    assert doc_id.startswith("doc_")
    assert ingest_res["status"] == "PUBLISHED"
    assert ingest_res["page_count"] == 1
    assert "separated_storage" in ingest_res
    assert Path(ingest_res["separated_storage"]["plain_text"]).exists()

    # 3. Test API endpoint GET /api/documents/{doc_id}/ocr-text
    resp_text = client.get(f"/api/documents/{doc_id}/ocr-text")
    assert resp_text.status_code == 200
    text_data = resp_text.json()
    assert text_data["document_id"] == doc_id
    assert "pages" in text_data or "full_text" in text_data

    # 4. Test API endpoint GET /api/documents/{doc_id}/llm-context
    resp_llm = client.get(f"/api/documents/{doc_id}/llm-context")
    assert resp_llm.status_code == 200
    assert "LEGAL RECORD" in resp_llm.text
    assert "START VERIFIED DOCUMENT TEXT" in resp_llm.text

    # 5. Test Download endpoints
    resp_dl_txt = client.get(f"/documents/{doc_id}/download/txt")
    assert resp_dl_txt.status_code == 200
    assert "HIGH COURT" in resp_dl_txt.text

    resp_dl_json = client.get(f"/documents/{doc_id}/download/json")
    assert resp_dl_json.status_code == 200
    json_dl = resp_dl_json.json()
    assert json_dl["document_id"] == doc_id


def test_api_document_upload(tmp_path):
    # Create test PDF
    pdf_path = tmp_path / "uploaded_fir.pdf"
    doc = fitz.open()
    p = doc.new_page()
    p.insert_text((72, 72), "FIRST INFORMATION REPORT\nUnder Section 154 Cr.P.C.\nPolice Station: Nagpur City.")
    doc.save(str(pdf_path))
    doc.close()

    # Upload via client
    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/api/documents/upload",
            files={"file": ("uploaded_fir.pdf", f, "application/pdf")},
            data={"title": "Nagpur FIR Record", "court": "Nagpur Police Station"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PUBLISHED"
    assert "separated_storage" in data
    assert Path(data["separated_storage"]["structured_json"]).exists()


def test_hot_folder_auto_sync(tmp_path):
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    incoming_file = INCOMING_DIR / "auto_incoming_test.pdf"

    # Create dummy pdf in incoming
    doc = fitz.open()
    p = doc.new_page()
    p.insert_text((72, 72), "Auto Ingested Document From Hot Folder Watcher.")
    doc.save(str(incoming_file))
    doc.close()

    # Run incoming folder scan
    results = scan_and_ingest_incoming_folder()
    assert len(results) >= 1
    assert results[0]["status"] == "PUBLISHED"
    assert not incoming_file.exists()  # Was moved and ingested


def test_case_linkages_and_fir_copies():
    from app.services.linkage_service import get_case_linkages, extract_case_identifiers
    
    # Test identifier extraction
    info = extract_case_identifiers("Nagpur (147/2002) FIR Copy English")
    assert info["case_number"] == "147/2002"
    assert info["police_station"] == "Nagpur"
    assert info["year"] == "2002"

    # Test case linkages for real cases
    linkages_4 = get_case_linkages("lt-4")
    assert linkages_4["primary_fir_number"] == "147/2002"
    assert len(linkages_4["fir_copies"]) >= 1
    assert "has_txt" in linkages_4["fir_copies"][0]

    linkages_19 = get_case_linkages("lt-19")
    assert linkages_19["primary_fir_number"] == "412/2007"
    assert len(linkages_19["fir_copies"]) >= 1


def test_document_download_and_view_txt():
    # Use real document in db
    resp = client.get("/documents/doc-Documents_1768563645_pdf/download/txt")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    assert len(resp.text) > 0

    resp_view = client.get("/documents/doc-Documents_1768563645_pdf/view/txt")
    assert resp_view.status_code == 200
    assert len(resp_view.text) > 0


def test_api_case_linkages():
    resp = client.get("/api/cases/lt-4/linkages")
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_fir_number"] == "147/2002"
    assert "fir_copies" in data
    assert "connected_cases" in data

