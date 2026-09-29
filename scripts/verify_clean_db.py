import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
try:
    p_ast = db.execute(text("SELECT count(*) FROM document_pages WHERE page_text LIKE '%*%'")).scalar()
    c_ast = db.execute(text("SELECT count(*) FROM document_chunks WHERE chunk_text LIKE '%*%'")).scalar()
    total_pages = db.execute(text("SELECT count(*) FROM document_pages")).scalar()
    total_chunks = db.execute(text("SELECT count(*) FROM document_chunks")).scalar()
    ph_pages = db.execute(text("SELECT count(*) FROM document_pages WHERE page_text LIKE '%Court Docket Exhibit%'")).scalar()
    
    print(f"Total Pages in DB: {total_pages}")
    print(f"Total Chunks in DB: {total_chunks}")
    print(f"Placeholder Pages Remaining: {ph_pages}")
    print(f"Pages with Asterisks: {p_ast}")
    print(f"Chunks with Asterisks: {c_ast}")
finally:
    db.close()
