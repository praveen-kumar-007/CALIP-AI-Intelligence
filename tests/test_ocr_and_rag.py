import pytest
from app.services.ocr_service import register_custom_ocr_handler, run_ocr_on_image
from app.services.vector_service import chunk_document_pages, generate_embedding
from app.services.rag_service import extractive_fallback_answer


def test_custom_ocr_handler_registration(tmp_path):
    # Register dummy custom OCR
    def my_ocr_func(img_path, page_num):
        return {
            "text": "STATE OF MAHARASHTRA VS ACCUSED RECORD",
            "confidence": 0.99,
            "method": "my_custom_ocr_test",
            "page_number": page_num,
        }

    register_custom_ocr_handler(my_ocr_func)
    
    # Test runner
    dummy_img = tmp_path / "test.png"
    dummy_img.write_bytes(b"\x89PNG\r\n\x1a\n")
    res = run_ocr_on_image(str(dummy_img), page_number=1)
    
    assert res["method"] == "my_custom_ocr_test"
    assert "STATE OF MAHARASHTRA" in res["text"]
    assert res["confidence"] == 0.99


def test_chunking_document_pages():
    pages = [
        {"page_number": 1, "text": "Section 406 IPC defines criminal breach of trust. Punishment extends to three years."},
        {"page_number": 2, "text": "Section 420 IPC defines cheating and dishonestly inducing delivery of property."},
    ]
    chunks = chunk_document_pages(pages, chunk_size=100, overlap=20)
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert "Section 406" in chunks[0]["chunk_text"]


def test_generate_embedding():
    emb = generate_embedding("Legal proceeding in High Court")
    assert isinstance(emb, list)
    assert len(emb) == 384  # all-MiniLM-L6-v2 dimension


def test_extractive_fallback_answer_with_sources():
    sources = [
        {
            "case_title": "Nagpur 147/2002",
            "case_number": "147/2002",
            "page_number": 1,
            "chunk_text": "Charge framed under Section 406 and 420 IPC against accused.",
        }
    ]
    ans = extractive_fallback_answer("What charges?", sources)
    assert "Nagpur 147/2002" in ans
    assert "Page 1" in ans
    assert "Charge framed" in ans
