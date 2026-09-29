import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.services.text_cleaner import sanitize_legal_text_for_rag_and_training

db = SessionLocal()
try:
    chunks = db.execute(text("SELECT id, chunk_text FROM document_chunks WHERE chunk_text LIKE '%*%'")).fetchall()
    print(f"Sanitizing {len(chunks)} chunks with asterisks...")
    for c in chunks:
        clean = sanitize_legal_text_for_rag_and_training(c.chunk_text)
        db.execute(text("UPDATE document_chunks SET chunk_text = :t WHERE id = :id"), {"t": clean, "id": c.id})
    db.commit()
    remaining = db.execute(text("SELECT count(*) FROM document_chunks WHERE chunk_text LIKE '%*%'")).scalar()
    print(f"Done! Remaining chunks with asterisks: {remaining}")
finally:
    db.close()
