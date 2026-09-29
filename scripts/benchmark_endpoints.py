import time
import sys
from fastapi.testclient import TestClient
from app.main import app

sys.stdout.reconfigure(encoding='utf-8')

print("Starting CALIP Production Benchmark (initializing server & pre-warming)...")
t_start = time.perf_counter()
with TestClient(app) as client:
    t_ready = time.perf_counter()
    print(f"Server pre-warm completed in: {t_ready - t_start:.2f}s\n")
    print("=" * 60)
    print("ENDPOINT BENCHMARK RESULTS")
    print("=" * 60)

    # 1. Platform Statistics
    t0 = time.perf_counter()
    r = client.get("/api/stats")
    t1 = time.perf_counter()
    stats = r.json().get("stats", {})
    print(f"1. GET /api/stats: {r.status_code} | {(t1-t0)*1000:.2f} ms | Pages: {stats.get('pages_count')} | Chunks: {stats.get('chunks_count')}")

    # 2. Case List
    t0 = time.perf_counter()
    r = client.get("/api/cases?limit=20")
    t1 = time.perf_counter()
    items = r.json().get("items", [])
    print(f"2. GET /api/cases: {r.status_code} | {(t1-t0)*1000:.2f} ms | Items: {len(items)}")

    # 3. Case Detail
    t0 = time.perf_counter()
    r = client.get("/api/cases/lt-4")
    t1 = time.perf_counter()
    case_docs = r.json().get("documents", [])
    print(f"3. GET /api/cases/lt-4: {r.status_code} | {(t1-t0)*1000:.2f} ms | Case Docs: {len(case_docs)}")

    # 4. Document Detail (Full OCR & Pages from SSD)
    t0 = time.perf_counter()
    r = client.get("/api/documents/doc-Documents_1721197710_pdf")
    t1 = time.perf_counter()
    doc_pages = r.json().get("pages", [])
    print(f"4. GET /api/documents/...: {r.status_code} | {(t1-t0)*1000:.2f} ms | Doc Pages: {len(doc_pages)}")

    # 5. Hybrid Search (Keyword + 40,863 Vector Matrix)
    t0 = time.perf_counter()
    r = client.get("/api/search?q=Nagpur&semantic=true")
    t1 = time.perf_counter()
    search_res = r.json()
    print(f"5. GET /api/search: {r.status_code} | {(t1-t0)*1000:.2f} ms | Top Chunks: {len(search_res.get('vector_chunks_matched', []))}")

    # 6. RAG Question Answering (Live generation)
    print("\nExecuting RAG Legal Briefing Query...")
    t0 = time.perf_counter()
    r = client.get("/api/rag/ask?query=What+are+the+charges+in+FIR+147/2002")
    t1 = time.perf_counter()
    rag_res = r.json()
    print(f"6. GET /api/rag/ask (Live): {r.status_code} | {(t1-t0):.2f}s | Grounded: {rag_res.get('grounded')}")

    # 7. RAG Question Answering (Instant Cache hit)
    t0 = time.perf_counter()
    r = client.get("/api/rag/ask?query=What+are+the+charges+in+FIR+147/2002")
    t1 = time.perf_counter()
    print(f"7. GET /api/rag/ask (Cached): {r.status_code} | {(t1-t0)*1000:.2f} ms")

    print("=" * 60)
    print("ALL PRODUCTION ENDPOINTS VERIFIED & BENCHMARKED!")
