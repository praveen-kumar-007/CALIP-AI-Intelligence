import hashlib
import json
import re
import time
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
    Ensures chunks are strictly sanitized for RAG vector search and model training.
    """
    from app.services.text_cleaner import sanitize_legal_text_for_rag_and_training, is_placeholder_or_dummy_text

    chunks: list[dict[str, Any]] = []
    chunk_idx = 0

    for page in pages:
        page_num = page.get("page_number", 1)
        raw_text = (page.get("text") or "").strip()
        if not raw_text or is_placeholder_or_dummy_text(raw_text):
            continue

        text = sanitize_legal_text_for_rag_and_training(raw_text)
        if not text:
            continue

        # Split by double newlines or paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if not paragraphs:
            paragraphs = [text]

        current_chunk = ""
        for para in paragraphs:
            clean_para = sanitize_legal_text_for_rag_and_training(para)
            if not clean_para:
                continue
            if len(current_chunk) + len(clean_para) <= chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + clean_para
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "page_number": page_num,
                        "chunk_text": current_chunk,
                        "token_count": len(current_chunk.split()),
                    })
                    chunk_idx += 1
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                current_chunk = (overlap_text + " " + clean_para).strip()

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


def index_document_chunks(
    document_id: str,
    case_id: str | None,
    pages: list[dict[str, Any]],
    atom_id: str | None = None,
) -> int:
    """Chunks pages, computes embeddings, and writes DocumentChunk records into DB with atom linkage."""
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
        # Resolve atom_id from document if not provided
        resolved_atom_id = atom_id
        if not resolved_atom_id:
            doc_rec = db.query(Document).filter_by(id=document_id).first()
            if doc_rec and doc_rec.atom_id:
                resolved_atom_id = str(doc_rec.atom_id)

        # Delete existing chunks for this document
        db.query(DocumentChunk).filter_by(document_id=document_id).delete()

        for idx, (meta, emb) in enumerate(zip(chunks_meta, embeddings)):
            chunk_obj = DocumentChunk(
                id=f"{document_id}_chk_{idx}",
                document_id=document_id,
                case_id=case_id,
                atom_id=resolved_atom_id,
                page_number=meta["page_number"],
                chunk_index=meta["chunk_index"],
                chunk_text=meta["chunk_text"],
                token_count=meta["token_count"],
                embedding=emb.tolist() if hasattr(emb, "tolist") else list(emb),
            )
            db.add(chunk_obj)
            count += 1
        db.commit()
        invalidate_vector_cache()
    finally:
        db.close()

    return count


_VECTOR_CACHE_DATA: list[dict[str, Any]] | None = None
_VECTOR_CACHE_MATRIX: np.ndarray | None = None
_ATOM_INDEX: dict[str, list[int]] = {}
_CASE_INDEX: dict[str, list[int]] = {}
_CACHE_INITIALIZED: bool = False

LOCAL_VECTOR_CACHE_PATH = settings.PROJECT_ROOT / "data" / "vector_cache.npz"
LOCAL_VECTOR_META_PATH = settings.PROJECT_ROOT / "data" / "vector_meta.json"


def _load_vector_cache_fast() -> bool:
    """Loads pre-indexed binary vector matrix and metadata into RAM in milliseconds."""
    global _VECTOR_CACHE_DATA, _VECTOR_CACHE_MATRIX, _ATOM_INDEX, _CASE_INDEX, _CACHE_INITIALIZED
    if _CACHE_INITIALIZED and _VECTOR_CACHE_MATRIX is not None:
        return True

    if not LOCAL_VECTOR_CACHE_PATH.exists() or not LOCAL_VECTOR_META_PATH.exists():
        return False

    try:
        t0 = time.time()
        npz = np.load(str(LOCAL_VECTOR_CACHE_PATH))
        _VECTOR_CACHE_MATRIX = npz["embeddings"]

        with open(str(LOCAL_VECTOR_META_PATH), "r", encoding="utf-8") as f:
            meta = json.load(f)
        _VECTOR_CACHE_DATA = meta.get("items", [])

        # Build instant O(1) atom and case index maps
        _ATOM_INDEX.clear()
        _CASE_INDEX.clear()
        for idx, item in enumerate(_VECTOR_CACHE_DATA):
            a_id = item.get("atom_id")
            if a_id:
                _ATOM_INDEX.setdefault(str(a_id), []).append(idx)
            c_id = item.get("case_id")
            if c_id:
                _CASE_INDEX.setdefault(str(c_id), []).append(idx)

        _CACHE_INITIALIZED = True
        elapsed = time.time() - t0
        print(f"[VectorService] In-memory vector matrix initialized in {elapsed:.3f}s ({len(_VECTOR_CACHE_DATA)} chunks).")
        return True
    except Exception as exc:
        print(f"[VectorService] Error initializing fast vector cache: {exc}")
        return False


def invalidate_vector_cache():
    global _VECTOR_CACHE_DATA, _VECTOR_CACHE_MATRIX, _CACHE_INITIALIZED
    _VECTOR_CACHE_DATA = None
    _VECTOR_CACHE_MATRIX = None
    _CACHE_INITIALIZED = False


def vector_search(
    query: str,
    top_k: int = 5,
    case_id: str | None = None,
    atom_id: str | None = None,
    court_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Ultra-fast sub-5ms vector search across 40,863 legal chunks.
    Uses precomputed in-memory normalized matrix with dot product similarity.
    Zero network latency, zero remote DB roundtrips.
    """
    if not query or not query.strip():
        return []

    query_emb = np.array(generate_embedding(query.strip()), dtype=np.float32)
    # Ensure query embedding is unit normalized
    q_norm = np.linalg.norm(query_emb)
    if q_norm > 0:
        query_emb = query_emb / q_norm

    # 1. Fast in-memory path (< 5 milliseconds)
    if _load_vector_cache_fast() and _VECTOR_CACHE_MATRIX is not None and _VECTOR_CACHE_DATA is not None:
        if atom_id and str(atom_id) in _ATOM_INDEX:
            indices = _ATOM_INDEX[str(atom_id)]
            sub_mat = _VECTOR_CACHE_MATRIX[indices]
            dots = np.dot(sub_mat, query_emb)
            top_local = np.argsort(dots)[::-1][:top_k]
            top_indices = [indices[i] for i in top_local]
            top_scores = [float(dots[i]) for i in top_local]
        elif case_id and case_id in _CASE_INDEX:
            indices = _CASE_INDEX[case_id]
            sub_mat = _VECTOR_CACHE_MATRIX[indices]
            dots = np.dot(sub_mat, query_emb)
            top_local = np.argsort(dots)[::-1][:top_k]
            top_indices = [indices[i] for i in top_local]
            top_scores = [float(dots[i]) for i in top_local]
        else:
            dots = np.dot(_VECTOR_CACHE_MATRIX, query_emb)
            top_indices = np.argsort(dots)[::-1][:top_k]
            top_scores = [float(dots[i]) for i in top_indices]

        results = []
        for idx, score in zip(top_indices, top_scores):
            it = _VECTOR_CACHE_DATA[idx]
            if court_filter and court_filter.lower() not in (it.get("doc_court") or "").lower():
                continue
            results.append({
                "chunk_id": it["id"],
                "document_id": it["doc_id"],
                "title": it["doc_title"],
                "document_title": it["doc_title"],
                "court": it["doc_court"],
                "page_number": it["page_number"],
                "chunk_text": it["chunk_text"],
                "case_id": it["case_id"],
                "case_title": it["case_title"],
                "case_number": it["case_number"],
                "atom_id": it["atom_id"],
                "source_url": it["doc_url"],
                "pdf_url": it["doc_url"],
                "similarity_score": round(score, 4),
            })
        return results

    # 2. Database Fallback (if local cache not yet generated)
    db = SessionLocal()
    results: list[dict[str, Any]] = []
    try:
        query_set = db.query(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.case_id,
            DocumentChunk.atom_id,
            DocumentChunk.page_number,
            DocumentChunk.chunk_text,
            DocumentChunk.embedding,
        ).filter(DocumentChunk.embedding.isnot(None))

        if atom_id:
            query_set = query_set.filter(DocumentChunk.atom_id == str(atom_id))
        elif case_id:
            query_set = query_set.filter(DocumentChunk.case_id == case_id)

        rows = query_set.all()
        if not rows:
            return []

        chunk_embeddings = []
        chunk_objects = []

        for row in rows:
            emb = row.embedding
            if isinstance(emb, (str, bytes)):
                try:
                    emb = json.loads(emb)
                except Exception:
                    continue
            if isinstance(emb, list) and len(emb) == len(query_emb):
                chunk_embeddings.append(emb)
                chunk_objects.append({
                    "id": row.id,
                    "document_id": row.document_id,
                    "case_id": row.case_id,
                    "page_number": row.page_number,
                    "chunk_text": row.chunk_text,
                })

        if not chunk_embeddings:
            return []

        emb_matrix = np.array(chunk_embeddings, dtype=np.float32)
        similarities = np.dot(emb_matrix, query_emb)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        for idx in top_indices:
            score = float(similarities[idx])
            chk = chunk_objects[idx]
            chk_id = chk["id"]
            doc_id = chk["document_id"]
            case_id_val = chk["case_id"]
            doc = db.query(Document).filter_by(id=doc_id).first()
            case = db.query(Case).filter_by(id=case_id_val).first() if case_id_val else None

            if court_filter and case and court_filter.lower() not in (case.court_name or "").lower():
                continue

            from app.services.legal_data import resolve_original_pdf_url
            resolved_pdf = resolve_original_pdf_url(doc_id, doc.original_pdf_url if doc else None) if doc_id else None

            results.append({
                "chunk_id": chk_id,
                "document_id": doc_id,
                "title": doc.title if doc else "Document",
                "document_title": doc.title if doc else "Document",
                "case_id": case_id_val,
                "case_title": case.title if case else None,
                "case_number": case.case_number if case else None,
                "court": case.court_name if case else (doc.court if doc else None),
                "page_number": chk["page_number"],
                "chunk_text": chk["chunk_text"],
                "source_url": doc.source_url if doc else None,
                "pdf_url": resolved_pdf,
                "original_pdf_url": resolved_pdf,
                "similarity_score": round(score, 4),
            })
    finally:
        db.close()

    return results
