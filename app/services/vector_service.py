from __future__ import annotations

import re
from typing import Any

import numpy as np

try:
    import torch
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except (ImportError, Exception):
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None
    torch = None

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import DocumentChunk, Document, Case

_MODEL: Any = None
MODEL_NAME = settings.EMBEDDING_MODEL_NAME


def get_embedding_model():
    global _MODEL
    if not HAS_SENTENCE_TRANSFORMERS:
        return None
    if _MODEL is None:
        try:
            if settings.EMBEDDING_DEVICE == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = settings.EMBEDDING_DEVICE
            print(f"[VectorService] Loading embedding model '{MODEL_NAME}' onto device: {device}")
            _MODEL = SentenceTransformer(MODEL_NAME, device=device)
        except Exception as exc:
            print(f"[VectorService] Warning loading model {MODEL_NAME}: {exc}")
            _MODEL = None
    return _MODEL


def chunk_document_pages(
    pages: list[dict[str, Any]],
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Splits page text into coherent semantic chunks.
    Preserves page number and approximate token/char counts.
    """
    chunks: list[dict[str, Any]] = []
    chunk_idx = 0

    for page in pages:
        page_num = page.get("page_number", 1)
        text = (page.get("text") or "").strip()
        if not text:
            continue

        # Split by double newlines or sentences
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if not paragraphs:
            paragraphs = [text]

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "chunk_text": current_chunk,
                        "token_count": len(current_chunk.split()),
                    })
                    chunk_idx += 1
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                current_chunk = (overlap_text + " " + para).strip()

        if current_chunk:
            chunks.append({
                "chunk_index": chunk_idx,
                "page_number": page_num,
                "chunk_text": current_chunk,
                "token_count": len(current_chunk.split()),
            })
            chunk_idx += 1

    return chunks


def _zero_dep_embedding(text: str, dim: int = 384) -> list[float]:
    """Lightweight deterministic normalized vector representation for serverless runtime."""
    import hashlib
    vec = [0.0] * dim
    words = re.findall(r"\w+", (text or "").lower())
    for w in words:
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = sum(x * x for x in vec) ** 0.5
    return [round(x / norm, 6) for x in vec] if norm > 0 else vec


def generate_embedding(text: str) -> list[float]:
    model = get_embedding_model()
    if model is not None:
        try:
            emb = model.encode(text, normalize_embeddings=True)
            return emb.tolist()
        except Exception:
            pass
    return _zero_dep_embedding(text)


def index_document_chunks(document_id: str, case_id: str | None, pages: list[dict[str, Any]]) -> int:
    """Chunks pages, computes embeddings, and writes DocumentChunk records into DB."""
    chunks_meta = chunk_document_pages(pages)
    if not chunks_meta:
        return 0

    texts = [c["chunk_text"] for c in chunks_meta]
    model = get_embedding_model()
    if model is not None:
        try:
            embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()
        except Exception:
            embeddings = [_zero_dep_embedding(t) for t in texts]
    else:
        embeddings = [_zero_dep_embedding(t) for t in texts]

    db = SessionLocal()
    count = 0
    try:
        # Delete existing chunks for this document
        db.query(DocumentChunk).filter_by(document_id=document_id).delete()

        for idx, (meta, emb) in enumerate(zip(chunks_meta, embeddings)):
            chunk_obj = DocumentChunk(
                id=f"{document_id}_chk_{idx}",
                document_id=document_id,
                case_id=case_id,
                page_number=meta["page_number"],
                chunk_index=meta["chunk_index"],
                chunk_text=meta["chunk_text"],
                token_count=meta["token_count"],
                embedding=emb.tolist() if hasattr(emb, "tolist") else list(emb),
            )
            db.add(chunk_obj)
            count += 1
        db.commit()
    finally:
        db.close()

    return count


def vector_search(
    query: str,
    top_k: int = 5,
    case_id: str | None = None,
    court_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Computes query embedding and performs cosine similarity search across all document chunks.
    """
    query_emb = np.array(generate_embedding(query), dtype=np.float32)

    db = SessionLocal()
    results: list[dict[str, Any]] = []
    try:
        query_set = db.query(DocumentChunk)
        if case_id:
            query_set = query_set.filter(DocumentChunk.case_id == case_id)

        all_chunks = query_set.all()
        if not all_chunks:
            return []

        chunk_embeddings = []
        chunk_objects = []

        for chk in all_chunks:
            if chk.embedding:
                chunk_embeddings.append(chk.embedding)
                chunk_objects.append(chk)

        if not chunk_embeddings:
            return []

        emb_matrix = np.array(chunk_embeddings, dtype=np.float32)  # (N, D)
        # Cosine similarity for normalized vectors is simply dot product
        similarities = np.dot(emb_matrix, query_emb)  # (N,)

        top_indices = np.argsort(similarities)[::-1][:top_k]

        for idx in top_indices:
            score = float(similarities[idx])
            chk = chunk_objects[idx]
            doc = db.query(Document).filter_by(id=chk.document_id).first()
            case = db.query(Case).filter_by(id=chk.case_id).first() if chk.case_id else None

            if court_filter and case and court_filter.lower() not in (case.court_name or "").lower():
                continue

            results.append({
                "chunk_id": chk.id,
                "document_id": chk.document_id,
                "document_title": doc.title if doc else "Document",
                "case_id": chk.case_id,
                "case_title": case.title if case else None,
                "case_number": case.case_number if case else None,
                "court": case.court_name if case else (doc.court if doc else None),
                "page_number": chk.page_number,
                "chunk_text": chk.chunk_text,
                "source_url": doc.source_url if doc else None,
                "pdf_url": doc.original_pdf_url if doc else None,
                "similarity_score": round(score, 4),
            })
    finally:
        db.close()

    return results
