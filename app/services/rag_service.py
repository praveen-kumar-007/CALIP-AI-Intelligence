from __future__ import annotations

import json
from typing import Any
import requests

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Case, Document, DocumentChunk
from app.services.vector_service import vector_search

from app.services.llm_provider import query_llm, get_active_model_name

OLLAMA_GENERATE_URL = settings.OLLAMA_GENERATE_URL
DEFAULT_MODEL = settings.OLLAMA_MODEL


def query_ollama(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout: int = settings.RAG_TIMEOUT_SECONDS,
) -> str | None:
    """Invokes production LLM (Groq, NVIDIA NIM, Gemini, or local Ollama)."""
    return query_llm(
        prompt=prompt,
        system_prompt="You are an expert AI Legal Intelligence Assistant for Indian court and legal proceedings. Answer strictly from sources with exact citations.",
        temperature=settings.RAG_TEMPERATURE,
        max_tokens=2048,
        timeout=timeout,
    )


def extractive_fallback_answer(query: str, sources: list[dict[str, Any]]) -> str:
    """Deterministic, extractive legal summary when LLM is unavailable."""
    if not sources:
        return "The available documents do not establish an answer to this query. Please verify the case number or review the document archive."

    top_snippet = sources[0]["chunk_text"]
    case_ref = sources[0].get("case_title") or sources[0].get("case_number") or "the case record"
    page_ref = sources[0].get("page_number", 1)

    return (
        f"Based on the available legal records for {case_ref} (Page {page_ref}), "
        f"the documented text indicates: \"{top_snippet[:400]}...\"\n\n"
        f"Please consult the verified source document below for the complete context."
    )


def ask_legal_question(
    query: str,
    case_id: str | None = None,
    court_filter: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """
    RAG Pipeline:
    1. Vector + Keyword Hybrid Search across document chunks
    2. Retrieve top-k evidence chunks with page numbers and source URLs
    3. Format source-grounded prompt for local Ollama LLM
    4. Return cited answer with explicit source provenance
    """
    limit_k = top_k if top_k is not None else settings.RAG_TOP_K
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "query": query,
            "answer": "Please provide a specific legal question or search query.",
            "sources": [],
            "grounded": False,
        }

    # 1. Retrieve evidence chunks
    retrieved_chunks = vector_search(
        query=cleaned_query,
        top_k=limit_k,
        case_id=case_id,
        court_filter=court_filter,
    )

    # If no vector chunks yet (e.g. database still harvesting), search cases and documents directly
    if not retrieved_chunks:
        db = SessionLocal()
        try:
            matched_cases = db.query(Case).filter(
                (Case.title.ilike(f"%{cleaned_query}%"))
                | (Case.case_number.ilike(f"%{cleaned_query}%"))
                | (Case.court_name.ilike(f"%{cleaned_query}%"))
                | (Case.summary.ilike(f"%{cleaned_query}%"))
            ).limit(3).all()

            for c in matched_cases:
                retrieved_chunks.append({
                    "chunk_id": f"case_{c.id}",
                    "document_id": None,
                    "document_title": c.title,
                    "case_id": c.id,
                    "case_title": c.title,
                    "case_number": c.case_number,
                    "court": c.court_name,
                    "page_number": 1,
                    "chunk_text": f"Case Number: {c.case_number}\nCourt: {c.court_name}\nTitle: {c.title}\nSummary: {c.summary or 'No summary recorded.'}",
                    "source_url": c.source_url,
                    "pdf_url": None,
                    "similarity_score": 0.85,
                })
        finally:
            db.close()

    if not retrieved_chunks:
        return {
            "query": cleaned_query,
            "answer": "The available documents do not establish the answer. No matching case, document, or judgment records were found in the current corpus.",
            "sources": [],
            "grounded": False,
        }

    # 2. Assemble context with provenance
    context_blocks = []
    for idx, item in enumerate(retrieved_chunks):
        c_title = item.get("case_title") or item.get("case_number") or "Case"
        d_title = item.get("document_title") or "Document"
        court = item.get("court") or "Court"
        page = item.get("page_number", 1)
        text = item.get("chunk_text", "")
        context_blocks.append(
            f"[Source {idx+1}]\nCase: {c_title}\nCourt: {court}\nDocument: {d_title}\nPage: {page}\nText:\n{text}"
        )

    context_str = "\n\n".join(context_blocks)

    system_prompt = (
        "You are an AI Legal Intelligence Assistant for the CALIP / Longtail Cases platform.\n"
        "RULES:\n"
        "1. Answer strictly based on the provided source documents.\n"
        "2. Always cite the exact Case, Court, Document Title, and Page Number from the sources.\n"
        "3. If the provided sources do not contain sufficient evidence to answer the question, explicitly state: 'The available documents do not establish the answer.'\n"
        "4. Do not invent facts, court outcomes, or legal advice.\n\n"
        f"SOURCES:\n{context_str}\n\n"
        f"QUESTION: {cleaned_query}\n\n"
        "ANSWER (with exact citations):"
    )

    # 3. Query local LLM
    llm_answer = query_ollama(system_prompt)
    if not llm_answer:
        llm_answer = extractive_fallback_answer(cleaned_query, retrieved_chunks)

    return {
        "query": cleaned_query,
        "answer": llm_answer,
        "sources": retrieved_chunks,
        "model": DEFAULT_MODEL if llm_answer and "Based on the available" not in llm_answer else "extractive_legal_rule",
        "grounded": True,
    }
