from pathlib import Path

import fitz

from app.services.pdf_ingest import extract_pdf_text, resolve_pdf_links_from_html


HTML_SAMPLE = """
<html><body>
<a href="/uploads/new_mis/MIS.pdf?v=1763839426">Summary All Cases</a>
<a href="/uploads/new_mis/DAILY%20COURT%20DATES.pdf?v=1790139276">Court Dates</a>
<a href="/documents/4">Nagpur case</a>
</body></html>
"""


def test_resolve_pdf_links_from_html():
    links = resolve_pdf_links_from_html(HTML_SAMPLE)
    assert len(links) == 2
    assert links[0]["label"] == "Summary All Cases"
    assert links[0]["url"].endswith("MIS.pdf?v=1763839426")


def test_extract_pdf_text_from_pdf(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "The court held that the application was maintainable.")
    doc.save(pdf_path)
    doc.close()
    text = extract_pdf_text(str(pdf_path))
    assert "maintainable" in text.lower()
