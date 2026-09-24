from app.services.longtail_scraper import extract_case_links, parse_longtail_document_page


SAMPLE_HTML = """
<html><head><title>Housefull24</title></head>
<body>
  <a href="/documents/4">Nagpur (147/2002)</a>
  <a href="/documents/11">Anand (361/2023)</a>
  <a href="/documents/25">Alipore (33/2002)</a>
  <a href="/uploads/new_mis/MIS.pdf?v=1763839426">Summary All Cases</a>
  <h1>Nagpur (147/2002)</h1>
  <p>FIR COPY A. English B. Marathi</p>
  <a href="/uploads/new_mis/charge-sheet.pdf">Charge Sheet</a>
</body>
</html>
"""


def test_extract_case_links_returns_structured_entries():
    result = extract_case_links(SAMPLE_HTML)
    assert len(result) >= 3
    assert result[0]["label"] == "Nagpur (147/2002)"
    assert result[0]["url"].endswith("/documents/4")


def test_parse_document_page_extracts_case_and_files():
    result = parse_longtail_document_page(SAMPLE_HTML)
    assert result["case_label"] == "Nagpur (147/2002)"
    assert result["case_number"] == "147/2002"
    assert result["court"] == "Nagpur"
    assert result["document_files"][0]["label"] == "Charge Sheet"


def test_parse_document_page_keeps_folder_links_for_fallback_ingestion():
    html = """
    <html><head><title>Housefull</title></head>
    <body>
      <h1>Nagpur (147/2002)</h1>
      <a href="/get-folder-documents/355">FIR COPY A. English B. Marathi</a>
      <a href="/get-folder-documents/354">Charge Sheet</a>
    </body>
    </html>
    """
    result = parse_longtail_document_page(html)
    assert result["folder_links"][0]["url"].endswith("/get-folder-documents/355")
    assert result["folder_links"][0]["label"] == "FIR COPY A. English B. Marathi"
