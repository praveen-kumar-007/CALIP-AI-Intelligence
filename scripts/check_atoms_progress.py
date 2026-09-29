import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
try:
    res = db.execute(text("""
        SELECT 
            a.fir_number,
            a.police_station,
            count(distinct d.id) as total_docs,
            count(distinct case when dp.page_text LIKE '%Court Docket Exhibit%' then d.id end) as docs_with_ph,
            count(distinct dp.id) as total_pages,
            count(distinct case when dp.page_text LIKE '%Court Docket Exhibit%' then dp.id end) as ph_pages
        FROM atoms a
        LEFT JOIN documents d ON (d.atom_id = a.id OR d.case_id = a.legacy_case_id)
        LEFT JOIN document_pages dp ON dp.document_id = d.id
        GROUP BY a.fir_number, a.police_station
        ORDER BY docs_with_ph ASC
    """)).fetchall()

    print("PILOT ATOMS STATUS:")
    for r in res:
        m = dict(r._mapping)
        fn = str(m["fir_number"])
        ps = str(m["police_station"])
        dwp = m["docs_with_ph"]
        php = m["ph_pages"] or 0
        totp = m["total_pages"] or 0
        print(f"FIR {fn:>4} ({ps:<15}): {dwp:>2} docs with PH (remaining {php:>4} PH pages / {totp:>4} total pages)")

    # Overall DB stats
    overall = db.execute(text("""
        SELECT 
            count(distinct d.id) as total_docs,
            count(distinct case when dp.page_text LIKE '%Court Docket Exhibit%' then d.id end) as docs_with_ph,
            count(distinct dp.id) as total_pages,
            count(distinct case when dp.page_text LIKE '%Court Docket Exhibit%' then dp.id end) as ph_pages
        FROM documents d
        LEFT JOIN document_pages dp ON dp.document_id = d.id
    """)).fetchone()
    print("-" * 60)
    print("OVERALL DB STATS:", dict(overall._mapping))
finally:
    db.close()
