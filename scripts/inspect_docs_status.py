import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
try:
    atoms = db.execute(text('SELECT id, fir_number, police_station, state FROM atoms ORDER BY id')).fetchall()
    print(f'Total Pilot Atoms: {len(atoms)}')

    doc_count = db.execute(text('SELECT count(*) FROM documents')).scalar()
    print(f'Total documents in DB: {doc_count}')

    atom_docs = db.execute(text("""
        SELECT d.id, d.title, d.case_id, d.page_count, d.original_pdf_url, d.source_url,
               (SELECT count(*) FROM document_pages dp WHERE dp.document_id = d.id) as stored_pages,
               (SELECT count(*) FROM document_pages dp WHERE dp.document_id = d.id AND dp.page_text LIKE '%Court Docket Exhibit%') as placeholder_pages
        FROM documents d
        ORDER BY d.id
    """)).fetchall()
    
    total_docs = len(atom_docs)
    docs_with_placeholders = [d for d in atom_docs if d.placeholder_pages > 0]
    docs_without_pages = [d for d in atom_docs if d.stored_pages == 0]
    
    print(f'Total Docs in DB: {total_docs}')
    print(f'Docs with placeholder pages: {len(docs_with_placeholders)}')
    print(f'Docs without any stored pages: {len(docs_without_pages)}')
    
    total_ph_pages = db.execute(text("SELECT count(*) FROM document_pages WHERE page_text LIKE '%Court Docket Exhibit%'")).scalar()
    print(f'Total placeholder pages across all docs: {total_ph_pages}')

    total_pages = db.execute(text('SELECT count(*) FROM document_pages')).scalar()
    print(f'Total document pages in DB: {total_pages}')

    # Let's inspect which documents belong to which atoms / cases
    case_ids = [a.id for a in atoms]
    print(f'Pilot Atom IDs: {case_ids[:5]}...')

    # Also check local PDF cache
    # Check PDF availability for placeholder docs
    docs_to_fix = db.execute(text("""
        SELECT d.id, d.title, d.case_id, d.atom_id, d.page_count, d.local_pdf_path, d.original_pdf_url, d.source_url,
               count(dp.id) as ph_count
        FROM documents d
        JOIN document_pages dp ON dp.document_id = d.id
        WHERE dp.page_text LIKE '%Court Docket Exhibit%'
        GROUP BY d.id, d.title, d.case_id, d.atom_id, d.page_count, d.local_pdf_path, d.original_pdf_url, d.source_url
        ORDER BY ph_count DESC
    """)).fetchall()

    print(f'Docs needing real OCR extraction: {len(docs_to_fix)}')
    has_local = 0
    has_url = 0
    for d in docs_to_fix:
        if d.local_pdf_path and os.path.exists(d.local_pdf_path):
            has_local += 1
        elif d.original_pdf_url or d.source_url:
            has_url += 1

    print(f'Docs with existing local PDF file: {has_local}')
    print(f'Docs with download URL: {has_url}')
    # Check atom link breakdown
    atom_linked = db.execute(text("""
        SELECT count(distinct d.id) 
        FROM documents d
        WHERE d.atom_id IS NOT NULL OR d.case_id IS NOT NULL
    """)).scalar()
    print(f'Documents linked to an atom or case: {atom_linked}')

    direct_atom_docs = db.execute(text("""
        SELECT a.id, a.fir_number, count(d.id) as doc_count,
               sum(case when dp.page_text LIKE '%Court Docket Exhibit%' then 1 else 0 end) as ph_pages
        FROM atoms a
        LEFT JOIN documents d ON d.atom_id = a.id
        LEFT JOIN document_pages dp ON dp.document_id = d.id
        GROUP BY a.id, a.fir_number
        ORDER BY doc_count DESC
    """)).fetchall()

    print('Pilot Atoms and their direct documents:')
    for a in direct_atom_docs:
        print(f'  Atom FIR {a.fir_number} (ID {str(a.id)[:8]}): {a.doc_count} docs, {a.ph_pages or 0} placeholder pages')

    # Also check via case_id
    case_atom_docs = db.execute(text("""
        SELECT count(distinct d.id)
        FROM documents d
        WHERE d.case_id IN (SELECT legacy_case_id FROM atoms WHERE legacy_case_id IS NOT NULL)
    """)).scalar()
    print(f'Documents linked via legacy_case_id: {case_atom_docs}')
finally:
    db.close()
