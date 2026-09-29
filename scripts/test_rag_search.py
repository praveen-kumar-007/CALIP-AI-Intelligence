import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_service import vector_search

queries = [
    "Section 420 cheating and fraud allegations",
    "bail granted conditions regular bail application",
    "recovery and property attachment proceedings"
]

for q in queries:
    print("=" * 60)
    print(f"QUERY: {q}")
    results = vector_search(q, top_k=2)
    print(f"Found {len(results)} results:")
    for i, r in enumerate(results):
        score = r.get("similarity_score", 0.0)
        doc_id = r.get("document_id")
        page = r.get("page_number")
        chunk_text = r.get("chunk_text", "")
        preview = chunk_text[:200].replace("\n", " ")
        print(f"  Result {i+1} [Doc: {doc_id}, Page: {page}, Score: {score:.3f}]:")
        print(f"    Text: {preview}...")
        assert "*" not in chunk_text, "Found asterisks in chunk text!"
print("=" * 60)
print("RAG VECTOR SEARCH CONFIRMED WORKING WITH CLEAN SANITIZED TEXT!")
