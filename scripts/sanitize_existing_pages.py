import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.services.text_cleaner import sanitize_legal_text_for_rag_and_training

db = SessionLocal()
try:
    # 1. Find all pages that contain asterisks or weird characters (excluding placeholder ones)
    rows = db.execute(text("""
        SELECT id, page_text 
        FROM document_pages 
        WHERE (page_text LIKE '%*%' OR page_text LIKE '%__{%' OR page_text LIKE '%# %')
          AND page_text NOT LIKE '%Court Docket Exhibit%'
    """)).fetchall()

    print(f"Found {len(rows)} existing genuine pages needing sanitization.")
    updated_count = 0

    for r in rows:
        cleaned = sanitize_legal_text_for_rag_and_training(r.page_text or "")
        db.execute(
            text("UPDATE document_pages SET page_text = :t, english_page_text = :t WHERE id = :id"),
            {"t": cleaned, "id": r.id}
        )
        updated_count += 1
        if updated_count % 50 == 0:
            db.commit()
            print(f"Sanitized {updated_count}/{len(rows)} pages...")

    db.commit()
    print(f"Successfully sanitized {updated_count} pages in database!")

    # Verify if any genuine pages still have asterisks
    remaining = db.execute(text("""
        SELECT count(*) FROM document_pages 
        WHERE page_text LIKE '%*%' AND page_text NOT LIKE '%Court Docket Exhibit%'
    """)).scalar()
    print(f"Remaining genuine pages with asterisks: {remaining}")

finally:
    db.close()
