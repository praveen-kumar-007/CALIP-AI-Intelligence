from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Case, Document, DocumentPage, Court
from app.services.legal_data import (
    get_all_cases,
    get_case_by_id,
    get_all_documents,
    get_document_by_id,
    get_all_judgments,
    get_judgment_by_id,
    get_all_orders,
    get_order_by_id,
    get_all_courts,
    get_platform_statistics,
    get_jurisdiction_summary,
)
from app.services.longtail_scraper import (
    get_cached_or_live_catalog,
    harvest_all_longtail_hierarchy,
    sync_catalog_to_database,
    crawl_case_document_page,
)
from app.services.pdf_ingest import process_and_ingest_pdf, ingest_local_pdf, DOWNLOADS_DIR, INCOMING_DIR
from app.services.ocr_service import (
    get_extracted_ocr_data,
    get_llm_ready_context,
    store_extracted_ocr_separately,
)
from app.services.rag_service import ask_legal_question
from app.services.vector_service import vector_search, index_document_chunks
from app.services.graph_service import get_case_graph_relationships, extract_entities_from_text, save_extracted_entities_and_relationships
from app.services.auto_sync import (
    start_auto_sync_worker,
    check_for_updates_and_sync,
    get_sync_status,
    scan_and_ingest_incoming_folder,
)
from app.services.summary_service import (
    generate_document_summary,
    get_document_summary,
    extractive_legal_summary,
    find_local_pdf_for_document,
    batch_extract_and_summarize_all,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready legal information and research system with AI-readable HTML, longtailcases hierarchy, pluggable OCR, vector search, and grounded RAG citations.",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Enable unrestricted Cross-Origin Resource Sharing (CORS) from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start background auto-sync worker on application import (disabled in serverless)
try:
    if settings.AUTO_SYNC_ENABLED and not getattr(settings, "IS_SERVERLESS", False):
        start_auto_sync_worker(interval_seconds=settings.AUTO_SYNC_INTERVAL_SECONDS)
except Exception as e:
    print(f"[Main] Auto-sync worker initialization warning: {e}")

STATIC_DIR = settings.STATIC_DIR
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


# ==========================================
# 1. SERVER-RENDERED PUBLIC HTML PAGES
# ==========================================

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    cases = get_all_cases(limit=10)
    stats = get_platform_statistics()
    jurisdictions = get_jurisdiction_summary()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "CALIP | Legal Case & Document Intelligence Platform",
            "cases": cases,
            "stats": stats,
            "jurisdictions": jurisdictions,
            "canonical_url": "https://longtailcases.com/",
        },
    )


@app.get("/cases", response_class=HTMLResponse)
def cases_page(
    request: Request,
    state: str | None = Query(default=None),
    q: str | None = Query(default=None),
):
    cases = get_all_cases(limit=60, state=state, query=q)
    return templates.TemplateResponse(
        request=request,
        name="cases.html",
        context={
            "title": f"Legal Cases {'- ' + state if state else ''} | CALIP",
            "cases": cases,
            "current_state": state,
            "query": q or "",
            "canonical_url": "https://longtailcases.com/cases",
        },
    )


@app.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail_page(request: Request, case_id: str):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case record not found.")
    return templates.TemplateResponse(
        request=request,
        name="case_detail.html",
        context={
            "title": f"{case['title']} ({case['case_number']}) | CALIP",
            "case": case,
            "canonical_url": f"https://longtailcases.com/cases/{case['id']}",
        },
    )


@app.get("/longtail", response_class=HTMLResponse)
def longtail_hierarchy_page(request: Request):
    catalog = get_cached_or_live_catalog()
    return templates.TemplateResponse(
        request=request,
        name="longtail.html",
        context={
            "title": "Longtail Cases Catalog Hierarchy | CALIP",
            "catalog": catalog,
            "canonical_url": "https://longtailcases.com/longtail",
        },
    )


@app.get("/documents", response_class=HTMLResponse)
def documents_page(request: Request, q: str | None = Query(default=None)):
    docs = get_all_documents(limit=50, query=q)
    return templates.TemplateResponse(
        request=request,
        name="documents.html",
        context={
            "title": "Legal Documents Archive | CALIP",
            "documents": docs,
            "query": q or "",
            "canonical_url": "https://longtailcases.com/documents",
        },
    )


@app.get("/documents/{document_id}", response_class=HTMLResponse)
def document_detail_page(request: Request, document_id: str):
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    case = get_case_by_id(doc["case_id"]) if doc.get("case_id") else None

    # Load OCR & LLM artifacts directly from Supabase PostgreSQL database
    ocr_artifact = get_extracted_ocr_data(document_id)
    llm_context = get_llm_ready_context(document_id)

    # Get complete text directly from database
    full_extracted_text = doc.get("extracted_text")
    if not full_extracted_text and ocr_artifact and ocr_artifact.get("full_text"):
        full_extracted_text = ocr_artifact["full_text"]

    # Auto-Extract if text is missing but remote PDF is available on longtailcases.com
    if not full_extracted_text or len(full_extracted_text.strip()) == 0:
        pdf_url = doc.get("original_pdf_url") or doc.get("pdf_url")
        if pdf_url and pdf_url.startswith("http"):
            try:
                ingest_res = process_and_ingest_pdf(
                    pdf_url=pdf_url,
                    title=doc.get("title") or "Document",
                    document_id=document_id,
                    case_id=doc.get("case_id"),
                    court=doc.get("court"),
                    document_type=doc.get("document_type") or "Document",
                    cleanup_temp_pdf=True,
                )
                if ingest_res and ingest_res.get("full_text"):
                    full_extracted_text = ingest_res["full_text"]
                doc = get_document_by_id(document_id) or doc
                # Reload artifacts after auto-ingest
                ocr_artifact = get_extracted_ocr_data(document_id) or ocr_artifact
                llm_context = get_llm_ready_context(document_id) or llm_context
            except Exception as e:
                print(f"[Main] Auto-ingest on view warning: {e}")

    # Re-verify ocr_artifact and llm_context are loaded
    if not ocr_artifact:
        ocr_artifact = get_extracted_ocr_data(document_id)
    if not llm_context:
        llm_context = get_llm_ready_context(document_id)

    # Load or provide instant AI Executive Brief / Legal Summary (instant sub-50ms render)
    ai_summary = get_document_summary(document_id)
    if not ai_summary and full_extracted_text and len(full_extracted_text.strip()) > 30:
        summary_text = extractive_legal_summary(
            text=full_extracted_text,
            title=doc.get("title") or "Document",
            court=doc.get("court"),
            document_type=doc.get("document_type"),
        )
        ai_summary = {
            "document_id": document_id,
            "summary_text": summary_text,
            "model": "deterministic_legal_engine",
        }

    # Load entities from graph if available
    graph_data = get_case_graph_relationships(doc["case_id"]) if doc.get("case_id") else {}
    doc_entities = [n for n in graph_data.get("nodes", []) if n.get("type") in ("PARTY", "SECTION", "COURT", "POLICE_STATION")][:10]

    from app.services.llm_provider import get_active_model_name, LLMProvider
    active_model_str = get_active_model_name()
    active_provider_str = LLMProvider.get_active_provider()

    return templates.TemplateResponse(
        request=request,
        name="document_detail.html",
        context={
            "title": f"{doc['title']} | CALIP Document",
            "document": doc,
            "case": case,
            "ocr_artifact": ocr_artifact,
            "llm_context": llm_context,
            "full_extracted_text": full_extracted_text,
            "ai_summary": ai_summary,
            "ai_model": active_model_str,
            "ai_provider": active_provider_str,
            "doc_entities": doc_entities,
            "has_txt_download": bool(full_extracted_text),
            "has_json_download": bool(ocr_artifact),
            "canonical_url": f"https://longtailcases.com/documents/{doc['id']}",
        },
    )


@app.get("/documents/{document_id}/download/txt")
def download_document_extracted_text(document_id: str):
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    text_content = doc.get("extracted_text")
    if not text_content and doc.get("pages"):
        text_content = "\n\n".join(p.get("page_text") or "" for p in doc["pages"])
    if not text_content:
        text_content = (
            f"CALIP LEGAL INTELLIGENCE ARCHIVE\n"
            f"Document ID: {document_id}\n"
            f"Title: {doc.get('title')}\n"
            f"Court: {doc.get('court') or 'Court of Record'}\n"
            f"Date: {doc.get('document_date') or 'Recorded'}\n"
            f"SHA-256 Digest: {doc.get('file_hash') or 'Verified Provenance'}\n"
            f"--------------------------------------------------\n\n"
            f"Document indexed and partitioned for RAG & LLM Legal Research.\n"
        )
    return Response(
        content=text_content,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{document_id}_extracted_text.txt"'},
    )


@app.get("/documents/{document_id}/view/txt", response_class=PlainTextResponse)
def view_document_extracted_text(document_id: str):
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    text_content = doc.get("extracted_text")
    if not text_content and doc.get("pages"):
        text_content = "\n\n".join(p.get("page_text") or "" for p in doc["pages"])
    if not text_content:
        text_content = f"No extracted text found in database for document {document_id}."
    return PlainTextResponse(content=text_content, media_type="text/plain; charset=utf-8")


@app.get("/documents/{document_id}/download/json")
def download_document_rag_json(document_id: str):
    ocr_data = get_extracted_ocr_data(document_id)
    if not ocr_data:
        doc = get_document_by_id(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        ocr_data = {
            "document_id": document_id,
            "title": doc.get("title"),
            "court": doc.get("court"),
            "full_text": doc.get("extracted_text") or "",
        }
    json_bytes = json.dumps(ocr_data, indent=2, ensure_ascii=False)
    return Response(
        content=json_bytes,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{document_id}_rag_artifact.json"'},
    )


@app.get("/api/cases/{case_id}/linkages")
def api_case_linkages(case_id: str):
    from app.services.linkage_service import get_case_linkages
    linkages = get_case_linkages(case_id)
    return JSONResponse(linkages)



@app.get("/judgments", response_class=HTMLResponse)
def judgments_page(request: Request):
    judgments = get_all_judgments()
    return templates.TemplateResponse(
        request=request,
        name="judgments.html",
        context={
            "title": "Library of Judgements & Precedents | CALIP",
            "judgments": judgments,
            "canonical_url": "https://longtailcases.com/judgments",
        },
    )


@app.get("/judgments/{judgment_id}", response_class=HTMLResponse)
def judgment_detail_page(request: Request, judgment_id: str):
    judgment = get_judgment_by_id(judgment_id)
    if not judgment:
        raise HTTPException(status_code=404, detail="Judgment not found.")
    return templates.TemplateResponse(
        request=request,
        name="judgment_detail.html",
        context={
            "title": f"{judgment['title']} | Judicial Precedent",
            "judgment": judgment,
            "canonical_url": f"https://longtailcases.com/judgments/{judgment_id}",
        },
    )


@app.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request):
    orders = get_all_orders()
    return templates.TemplateResponse(
        request=request,
        name="orders.html",
        context={
            "title": "Court Orders & Directions | CALIP",
            "orders": orders,
            "canonical_url": "https://longtailcases.com/orders",
        },
    )


@app.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail_page(request: Request, order_id: str):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return templates.TemplateResponse(
        request=request,
        name="order_detail.html",
        context={
            "title": f"Court Order {order_id} | CALIP",
            "order": order,
            "canonical_url": f"https://longtailcases.com/orders/{order_id}",
        },
    )


@app.get("/courts", response_class=HTMLResponse)
def courts_page(request: Request):
    courts = get_all_courts()
    return templates.TemplateResponse(
        request=request,
        name="courts.html",
        context={
            "title": "Courts & Jurisdictions | CALIP",
            "courts": courts,
            "canonical_url": "https://longtailcases.com/courts",
        },
    )


@app.get("/acts", response_class=HTMLResponse)
def acts_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="acts.html",
        context={
            "title": "Statutory Acts & Legal Provisions | CALIP",
            "canonical_url": "https://longtailcases.com/acts",
        },
    )


@app.get("/sections", response_class=HTMLResponse)
def sections_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="acts.html",
        context={
            "title": "Legal Sections & Provisions | CALIP",
            "canonical_url": "https://longtailcases.com/sections",
        },
    )


@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request, q: str | None = Query(default=None)):
    results = []
    vector_results = []
    if q and q.strip():
        results = get_all_cases(limit=10, query=q.strip())
        vector_results = vector_search(query=q.strip(), top_k=5)

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "title": f"Search '{q}' | CALIP Legal Intelligence" if q else "Legal Hybrid Search | CALIP",
            "query": q or "",
            "results": results,
            "vector_results": vector_results,
            "canonical_url": "https://longtailcases.com/search",
        },
    )


@app.get("/ai-research", response_class=HTMLResponse)
def ai_research_page(request: Request, query: str | None = Query(default=None)):
    result = None
    if query and query.strip():
        result = ask_legal_question(query=query.strip(), top_k=4)

    return templates.TemplateResponse(
        request=request,
        name="ai_research.html",
        context={
            "title": f"AI Legal Research: {query[:40]}... | CALIP" if query else "AI Case Intelligence & Citation Assistant | CALIP",
            "query": query or "",
            "result": result,
            "canonical_url": "https://longtailcases.com/ai-research",
        },
    )


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page(request: Request):
    stats = get_platform_statistics()
    sync_status = get_sync_status()
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "title": "Pipeline & OCR Dashboard | CALIP Admin",
            "stats": stats,
            "sync_status": sync_status,
            "canonical_url": "https://longtailcases.com/admin/dashboard",
        },
    )


@app.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "title": "About & Provenance | CALIP Legal Intelligence",
            "canonical_url": "https://longtailcases.com/about",
        },
    )


# ==========================================
# 2. SEO, ROBOTS & SITEMAPS
# ==========================================

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    content = """User-agent: *
Allow: /
Allow: /cases
Allow: /cases/
Allow: /judgments
Allow: /judgments/
Allow: /orders
Allow: /orders/
Allow: /documents
Allow: /documents/
Allow: /longtail
Allow: /courts
Allow: /acts
Allow: /sections
Allow: /search
Allow: /api
Allow: /api/
Allow: /api/open/
Allow: /llms.txt
Allow: /llms-full.txt
Allow: /download/
Disallow: /admin/
Disallow: /private/
Disallow: /internal/
Disallow: /api/admin/
Disallow: /database/
Disallow: /backups/
Disallow: /logs/
Disallow: /.env

# Unrestricted Open Access for Free Claude, ChatGPT, Perplexity & AI Crawlers
User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: Diffbot
Allow: /

User-agent: cohere-ai
Allow: /

Sitemap: https://longtailcases.com/sitemap.xml
Sitemap: https://longtailcases.com/sitemap-cases.xml
Sitemap: https://longtailcases.com/sitemap-documents.xml
Sitemap: https://longtailcases.com/sitemap-judgments.xml
Sitemap: https://longtailcases.com/sitemap-orders.xml
"""
    return PlainTextResponse(content=content)


@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """
    Standard LLM site manifest following the llms.txt standard.
    Allows Claude, ChatGPT, Perplexity, and external autonomous AI agents to discover,
    crawl, and read all legal data without authentication or API keys.
    """
    content = """# CALIP - Cognitive Atomic Legal Intelligence Platform
> Open, source-grounded legal case and document repository structuring cases, judgments, orders, applications, and documents from longtailcases.com with cryptographic provenance and page-level citations.

All data on this platform is completely open, public, and unauthenticated. AI agents, web crawlers, and LLM-assisted search systems (such as Claude, ChatGPT, Perplexity, Gemini, etc.) are explicitly permitted and encouraged to crawl, index, read, and extract all database records and OCR files without requiring any API keys.

## Fast Links for LLMs & Crawlers
- [Full Knowledge Corpus in Markdown](/llms-full.txt): Complete concatenated text of all cases and extracted documents in Markdown for direct context ingestion.
- [Full Database JSON Dump](/api/open/dump): Complete single-payload unauthenticated database dump (cases, documents, courts, stats).
- [Open Cases API](/api/open/cases): Full list of cases with metadata and document counts.
- [Open Documents API](/api/open/documents): Full list of documents with OCR status, page counts, and download links.
- [Open Q&A / Ask Engine](/api/open/ask?query={query}): Query the grounded legal RAG pipeline with citations and text snippets.

## Direct Markdown Endpoints for AI Web Browsing
- Case Markdown: `/api/cases/{case_id}/markdown`
- Document Markdown & Full OCR: `/api/documents/{document_id}/markdown`
- Document LLM Context Block: `/api/documents/{document_id}/llm-context`

## Public REST Endpoints (No Authentication Required)
- `GET /api/open/dump`: Complete database dump (cases, documents, courts, stats)
- `GET /api/open/cases`: List of all cases with full metadata
- `GET /api/open/documents`: List of all documents with page counts & OCR status
- `GET /api/open/ask?query=...`: Grounded RAG query endpoint with citations
- `GET /api/open/schema`: Machine-readable database schema and endpoint map
- `GET /api/search?q=...&semantic=true`: Hybrid keyword and semantic vector search
- `GET /api/cases`: Paginated case list
- `GET /api/cases/{case_id}`: Case details by ID
- `GET /api/cases/{case_id}/documents`: Documents attached to a case
- `GET /api/cases/{case_id}/relationships`: Entity relationship graph
- `GET /api/documents`: Paginated document list
- `GET /api/documents/{document_id}`: Document record by ID
- `GET /api/documents/{document_id}/ocr-text`: Verified OCR extracted text JSON
- `GET /api/longtail/catalog`: Hierarchical category catalog

## AI Agent Ingestion Instructions
1. To obtain a fast complete snapshot of all legal records, fetch `/llms-full.txt` or `/api/open/dump`.
2. To research a specific case, fetch `/api/cases/{case_id}/markdown`.
3. To read the verbatim legal text or OCR extracted from any document (including hundreds of pages of filings or FIRs), fetch `/api/documents/{document_id}/markdown` or `/api/documents/{document_id}/llm-context`.
4. No API keys, tokens, or headers are required. CORS is completely open (`*`).
"""
    return PlainTextResponse(content=content, media_type="text/plain; charset=utf-8")


@app.get("/llms-full.txt", response_class=PlainTextResponse)
async def llms_full_txt():
    """
    Concatenated full plain-text knowledge base in Markdown for direct LLM ingestion.
    Allows web-browsing LLMs (Free Claude, ChatGPT, etc.) to read the entire platform in one request.
    """
    cases = get_all_cases(limit=100)
    docs = get_all_documents(limit=100)
    stats = get_platform_statistics()

    md_lines = [
        "# CALIP PLATFORM COMPLETE KNOWLEDGE CORPUS",
        f"Generated: {datetime.datetime.utcnow().isoformat()}Z",
        f"Platform Statistics: {stats.get('total_cases', len(cases))} Cases | {stats.get('total_documents', len(docs))} Documents | {stats.get('total_pages_ocr', 0)} Pages OCR Indexed",
        "",
        "---",
        "## I. LEGAL CASES REPOSITORY",
        "",
    ]

    for c in cases:
        md_lines.append(f"### Case: {c.get('title')}")
        md_lines.append(f"- **ID:** `{c.get('id')}`")
        md_lines.append(f"- **Case Number:** {c.get('case_number')}")
        md_lines.append(f"- **Court:** {c.get('court') or 'Not Specified'}")
        md_lines.append(f"- **Bench:** {c.get('bench') or 'Not Specified'}")
        md_lines.append(f"- **Filing Date:** {c.get('filing_date') or 'Not Specified'}")
        md_lines.append(f"- **Status:** {c.get('status') or 'Pending'}")
        md_lines.append(f"- **Subject / Category:** {c.get('subject') or 'General'}")
        md_lines.append(f"- **Source URL:** {c.get('source_url') or 'N/A'}")
        md_lines.append(f"- **Summary:** {c.get('summary') or 'No summary recorded.'}")
        md_lines.append(f"- **Markdown URL:** `/api/cases/{c.get('id')}/markdown`")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("## II. LEGAL DOCUMENTS & EXTRACTED OCR CORPUS")
    md_lines.append("")

    for d in docs:
        doc_id = d.get("id")
        md_lines.append(f"### Document: {d.get('title')}")
        md_lines.append(f"- **ID:** `{doc_id}`")
        md_lines.append(f"- **Case Reference:** `{d.get('case_id')}`")
        md_lines.append(f"- **Court:** {d.get('court') or 'Not Specified'}")
        md_lines.append(f"- **Type:** {d.get('document_type') or 'Document'}")
        md_lines.append(f"- **Page Count:** {d.get('page_count', 1)}")
        md_lines.append(f"- **OCR Status:** {d.get('ocr_status')}")
        md_lines.append(f"- **Extraction Method:** {d.get('extraction_method') or 'Windows Native OCR'}")
        md_lines.append(f"- **Direct Markdown:** `/api/documents/{doc_id}/markdown`")
        md_lines.append(f"- **Direct Download:** `/download/{doc_id}`")

        # Include text preview or extracted context
        ocr_data = get_extracted_ocr_data(doc_id)
        if ocr_data and ocr_data.get("full_text"):
            sample_text = ocr_data["full_text"][:3000].strip()
            md_lines.append("#### Verbatim OCR Excerpt:")
            md_lines.append("```text")
            md_lines.append(sample_text)
            if len(ocr_data["full_text"]) > 3000:
                md_lines.append(f"... [Truncated. Full {len(ocr_data['full_text'])} characters available at /api/documents/{doc_id}/markdown]")
            md_lines.append("```")
        elif d.get("extracted_text"):
            sample_text = d["extracted_text"][:3000].strip()
            md_lines.append("#### Verbatim Text Excerpt:")
            md_lines.append("```text")
            md_lines.append(sample_text)
            if len(d["extracted_text"]) > 3000:
                md_lines.append(f"... [Truncated. Full {len(d['extracted_text'])} characters available at /api/documents/{doc_id}/markdown]")
            md_lines.append("```")
        else:
            md_lines.append("*Full text extraction queued / available via re-extract endpoint.*")
        md_lines.append("")

    full_md = "\n".join(md_lines)
    return PlainTextResponse(content=full_md, media_type="text/markdown; charset=utf-8")


@app.get("/sitemap.xml", response_class=HTMLResponse)
async def sitemap_index():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://longtailcases.com/sitemap-cases.xml</loc></sitemap>
  <sitemap><loc>https://longtailcases.com/sitemap-documents.xml</loc></sitemap>
  <sitemap><loc>https://longtailcases.com/sitemap-judgments.xml</loc></sitemap>
  <sitemap><loc>https://longtailcases.com/sitemap-orders.xml</loc></sitemap>
</sitemapindex>"""
    return HTMLResponse(content=xml, media_type="application/xml")


@app.get("/sitemap-cases.xml", response_class=HTMLResponse)
async def sitemap_cases():
    cases = get_all_cases(limit=100)
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for c in cases:
        xml += f"  <url><loc>https://longtailcases.com/cases/{c['id']}</loc><changefreq>weekly</changefreq></url>\n"
    xml += "</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")


@app.get("/sitemap-documents.xml", response_class=HTMLResponse)
async def sitemap_documents():
    docs = get_all_documents(limit=100)
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for d in docs:
        xml += f"  <url><loc>https://longtailcases.com/documents/{d['id']}</loc><changefreq>monthly</changefreq></url>\n"
    xml += "</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")


@app.get("/sitemap-judgments.xml", response_class=HTMLResponse)
async def sitemap_judgments():
    judgs = get_all_judgments(limit=50)
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for j in judgs:
        xml += f"  <url><loc>https://longtailcases.com/judgments/{j['id']}</loc></url>\n"
    xml += "</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")


@app.get("/sitemap-orders.xml", response_class=HTMLResponse)
async def sitemap_orders():
    orders = get_all_orders(limit=50)
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for o in orders:
        xml += f"  <url><loc>https://longtailcases.com/orders/{o['id']}</loc></url>\n"
    xml += "</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")


# ==========================================
# 3. PUBLIC REST API ENDPOINTS
# ==========================================

@app.get("/api")
async def api_documentation():
    return JSONResponse({
        "platform": "CALIP Legal Intelligence Platform",
        "version": "1.0.0",
        "description": "Public read-only REST API exposing cases, documents, judgments, orders, courts, search, and RAG answer engine. Completely unauthenticated and open for all AI agents and web crawlers.",
        "ai_crawling_manifests": {
            "llms_manifest": "/llms.txt",
            "llms_full_markdown_corpus": "/llms-full.txt",
            "robots_policy": "/robots.txt",
            "sitemap_index": "/sitemap.xml",
        },
        "open_unauthenticated_endpoints": {
            "full_database_dump": "/api/open/dump",
            "all_cases": "/api/open/cases",
            "all_documents": "/api/open/documents",
            "open_ask_engine": "/api/open/ask?query={query}",
            "machine_schema": "/api/open/schema",
            "case_as_markdown": "/api/cases/{case_id}/markdown",
            "document_as_markdown": "/api/documents/{document_id}/markdown",
            "document_llm_context": "/api/documents/{document_id}/llm-context",
        },
        "endpoints": {
            "cases": "/api/cases",
            "case_detail": "/api/cases/{case_id}",
            "case_documents": "/api/cases/{case_id}/documents",
            "case_relationships": "/api/cases/{case_id}/relationships",
            "documents": "/api/documents",
            "document_detail": "/api/documents/{document_id}",
            "judgments": "/api/judgments",
            "judgment_detail": "/api/judgments/{judgment_id}",
            "orders": "/api/orders",
            "courts": "/api/courts",
            "search": "/api/search?q={query}",
            "rag_qa": "/api/rag/ask?query={query}",
            "longtail_catalog": "/api/longtail/catalog",
            "longtail_harvest": "/api/longtail/harvest (POST)",
            "custom_ocr": "/api/ocr/custom (POST)",
        }
    })


@app.get("/api/cases")
async def api_cases_list(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    state: str | None = Query(default=None),
    q: str | None = Query(default=None),
):
    cases = get_all_cases(limit=limit, offset=offset, state=state, query=q)
    return JSONResponse({"count": len(cases), "offset": offset, "limit": limit, "items": cases})


@app.get("/api/cases/{case_id}")
async def api_case_detail(case_id: str):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case record not found.")
    return JSONResponse(case)


@app.get("/api/cases/{case_id}/documents")
async def api_case_documents(case_id: str):
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")
    return JSONResponse({"case_id": case_id, "documents": case.get("documents", [])})


@app.get("/api/cases/{case_id}/relationships")
async def api_case_relationships(case_id: str):
    graph = get_case_graph_relationships(case_id)
    return JSONResponse(graph)


@app.get("/api/documents")
async def api_documents_list(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    q: str | None = Query(default=None),
):
    docs = get_all_documents(limit=limit, offset=offset, query=q)
    return JSONResponse({"count": len(docs), "offset": offset, "limit": limit, "items": docs})


@app.get("/api/documents/{document_id}")
async def api_document_detail(document_id: str):
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return JSONResponse(doc)


@app.get("/api/judgments")
async def api_judgments_list(limit: int = 50, offset: int = 0):
    judgs = get_all_judgments(limit=limit, offset=offset)
    return JSONResponse({"count": len(judgs), "items": judgs})


@app.get("/api/judgments/{judgment_id}")
async def api_judgment_detail(judgment_id: str):
    j = get_judgment_by_id(judgment_id)
    if not j:
        raise HTTPException(status_code=404, detail="Judgment not found.")
    return JSONResponse(j)


@app.get("/api/orders")
async def api_orders_list(limit: int = 50, offset: int = 0):
    ords = get_all_orders(limit=limit, offset=offset)
    return JSONResponse({"count": len(ords), "items": ords})


@app.get("/api/courts")
async def api_courts_list():
    courts = get_all_courts()
    return JSONResponse({"count": len(courts), "items": courts})


@app.get("/api/search")
async def api_search_endpoint(
    q: str = Query(default=""),
    semantic: bool = Query(default=True),
):
    cleaned = q.strip()
    case_results = get_all_cases(limit=10, query=cleaned) if cleaned else []
    vector_results = vector_search(query=cleaned, top_k=5) if cleaned and semantic else []

    return JSONResponse({
        "query": q,
        "cases_matched": case_results,
        "vector_chunks_matched": vector_results,
    })


class QuestionRequest(BaseModel):
    query: str
    case_id: str | None = None
    court: str | None = None


@app.get("/api/rag/ask")
async def api_rag_ask_get(query: str = Query(...)):
    ans = ask_legal_question(query=query)
    return JSONResponse(ans)


@app.post("/api/rag/ask")
async def api_rag_ask_post(payload: QuestionRequest):
    ans = ask_legal_question(query=payload.query, case_id=payload.case_id, court_filter=payload.court)
    return JSONResponse(ans)


@app.get("/api/longtail/catalog")
async def api_longtail_catalog():
    catalog = get_cached_or_live_catalog()
    return JSONResponse(catalog)


@app.get("/api/sync/status")
def api_sync_status():
    return JSONResponse(get_sync_status())


@app.post("/api/sync/trigger")
def api_sync_trigger():
    res = check_for_updates_and_sync(auto_ingest_new_pdfs=True)
    return JSONResponse(res)


@app.post("/api/longtail/harvest")
def api_longtail_harvest(limit: int | None = Query(default=44)):
    catalog = harvest_all_longtail_hierarchy(limit_cases=limit)
    docs_synced = sync_catalog_to_database(catalog)
    return JSONResponse({
        "status": "success",
        "cases_harvested": catalog.get("total_cases"),
        "documents_synced": docs_synced,
    })


@app.post("/api/pdf/ingest-url")
async def api_pdf_ingest_url(
    pdf_url: str = Form(...),
    title: str = Form(default="Legal Document"),
    document_type: str = Form(default="Document"),
    case_id: str | None = Form(default=None),
):
    result = process_and_ingest_pdf(
        pdf_url=pdf_url,
        title=title,
        document_type=document_type,
        case_id=case_id,
    )
    return JSONResponse(result)


@app.post("/api/documents/upload")
async def api_document_upload(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    case_id: str | None = Form(default=None),
    court: str | None = Form(default=None),
    document_type: str = Form(default="Document"),
):
    """
    Direct PDF File Upload Endpoint:
    Accepts any uploaded PDF file, saves it to data/downloads,
    triggers high-level multi-stage OCR with layout extraction,
    stores clean text & RAG artifacts separately,
    and updates vector embeddings + knowledge graph immediately.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for upload.")

    safe_name = f"upload_{int(datetime.datetime.now().timestamp())}_{re.sub(r'[^A-Za-z0-9_.-]', '_', file.filename)}"
    temp_dir = Path(tempfile.gettempdir()) / "calip_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    dest_path = temp_dir / safe_name

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    doc_title = title.strip() if title and title.strip() else file.filename.rsplit(".", 1)[0].replace("_", " ").title()

    try:
        result = ingest_local_pdf(
            local_path=str(dest_path),
            title=doc_title,
            case_id=case_id,
            court=court,
            document_type=document_type,
        )
        return JSONResponse(result)
    finally:
        if dest_path.exists():
            try:
                dest_path.unlink()
            except Exception:
                pass


@app.get("/api/documents/{document_id}/ocr-text")
def api_document_ocr_text(document_id: str):
    """
    Returns separately stored high-level OCR text and layout metadata for RAG and external LLMs.
    """
    data = get_extracted_ocr_data(document_id)
    if data:
        return JSONResponse(data)

    # Fallback to DB
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return JSONResponse({
        "document_id": document_id,
        "title": doc.get("title"),
        "full_text": doc.get("extracted_text"),
        "page_count": doc.get("page_count", 0),
        "ocr_required": doc.get("ocr_required", False),
        "average_confidence": doc.get("ocr_confidence", 0.9),
        "source": "database_fallback",
    })


@app.get("/api/documents/{document_id}/llm-context")
def api_document_llm_context(document_id: str):
    """
    Returns verified citation-grounded LLM context block designed for direct ingestion into LLM prompts.
    """
    context_text = get_llm_ready_context(document_id)
    if context_text:
        return PlainTextResponse(content=context_text, media_type="text/markdown; charset=utf-8")

    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    fallback_text = (
        f"# LEGAL RECORD: {doc.get('title')}\n"
        f"**Case Reference:** {doc.get('case_id') or 'Unassigned'}\n"
        f"**Court:** {doc.get('court') or 'Court'}\n\n"
        f"--- START DOCUMENT TEXT ---\n"
        f"{doc.get('extracted_text') or 'No text available.'}\n"
        f"--- END DOCUMENT TEXT ---\n"
    )
    return PlainTextResponse(content=fallback_text, media_type="text/markdown; charset=utf-8")


@app.get("/api/pipeline/stats")
def api_pipeline_stats():
    """Returns dynamic statistics on database OCR records, incoming folder, and sync status."""
    stats = get_platform_statistics()
    sync_status = get_sync_status()
    incoming_files = list(INCOMING_DIR.glob("*.*")) if INCOMING_DIR.exists() else []

    return JSONResponse({
        "ocr_extracted_documents_count": stats.get("ocr_documents_count", stats.get("documents_count", 0)),
        "incoming_queue_files_count": len(incoming_files),
        "platform_stats": stats,
        "sync_status": sync_status,
        "ocr_storage_dir": "PostgreSQL Database (Supabase)",
        "incoming_dir": "Cloud Stream (Supabase)",
    })


@app.post("/api/ocr/custom")
async def api_custom_ocr_ingest(
    request: Request,
    document_id: str = Form(...),
    text: str = Form(default=""),
    method: str = Form(default="my_ocr"),
    confidence: float = Form(default=0.95),
):
    """
    Direct ingestion endpoint for 'My OCR':
    Accepts text extracted by user's OCR engine, updates the document record,
    stores separately, re-chunks, and updates vector embeddings immediately for RAG answering.
    Redirects cleanly back to the document view for browser form posts, or returns JSON for API calls.
    """
    is_browser_form = "text/html" in request.headers.get("accept", "") and not request.headers.get("x-requested-with")

    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        if text.strip():
            doc.extracted_text = text
            doc.extraction_method = method
            doc.ocr_status = "completed"
            doc.ocr_confidence = confidence

            # Save as page 1 or replace pages
            db.query(DocumentPage).filter_by(document_id=document_id).delete()
            db.add(DocumentPage(
                id=f"{document_id}_p1",
                document_id=document_id,
                page_number=1,
                page_text=text,
                has_images=True,
                ocr_confidence=confidence,
                extraction_method=method,
            ))
            db.commit()

            # Store separately for RAG & LLMs
            fake_extraction = {
                "page_count": 1,
                "ocr_required": True,
                "ocr_pages_count": 1,
                "average_confidence": confidence,
                "total_characters": len(text),
                "total_words": len(text.split()),
                "pages": [{
                    "page_number": 1,
                    "text": text,
                    "confidence": confidence,
                    "method": method,
                    "ocr_applied": True,
                }],
                "full_text": text,
            }
            store_extracted_ocr_separately(
                document_id=document_id,
                title=doc.title,
                extraction_res=fake_extraction,
                case_id=doc.case_id,
                court=doc.court,
                file_hash=doc.file_hash,
                original_url=doc.original_pdf_url,
            )

            # Extract entities and re-chunk/embed
            ents = extract_entities_from_text(text, document_id=document_id, page_number=1)
            save_extracted_entities_and_relationships(doc.case_id, document_id, ents)
            chunks_count = index_document_chunks(document_id, doc.case_id, [{"page_number": 1, "text": text}])

            if is_browser_form:
                return RedirectResponse(url=f"/documents/{document_id}#tab-extracted-text", status_code=303)

            return JSONResponse({
                "status": "success",
                "document_id": document_id,
                "method": method,
                "chunks_created": chunks_count,
                "message": "Custom OCR text successfully ingested, stored separately, and indexed into vector store.",
            })
        else:
            # Trigger pipeline on PDF if local file or url is present
            res = None
            if doc.local_pdf_path and os.path.exists(doc.local_pdf_path):
                res = ingest_local_pdf(
                    local_path=doc.local_pdf_path,
                    title=doc.title,
                    document_id=doc.id,
                    case_id=doc.case_id,
                    court=doc.court,
                    document_type=doc.document_type,
                    original_pdf_url=doc.original_pdf_url,
                )
            elif doc.original_pdf_url:
                res = process_and_ingest_pdf(
                    pdf_url=doc.original_pdf_url,
                    title=doc.title,
                    document_id=doc.id,
                    case_id=doc.case_id,
                    court=doc.court,
                    document_type=doc.document_type,
                )

            if is_browser_form:
                return RedirectResponse(url=f"/documents/{document_id}#tab-extracted-text", status_code=303)

            if res:
                return JSONResponse(res)
            return JSONResponse({"status": "no_text_or_pdf_available"})
    finally:
        db.close()


@app.post("/api/documents/{document_id}/re-extract")
async def api_document_reextract(document_id: str):
    """
    Asynchronous / AJAX endpoint for triggering full document OCR & metadata extraction.
    Uses native Windows OCR (winocr) or PyMuPDF, extracts layout, updates entities,
    and partitions text into separated storage.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        local_path = doc.local_pdf_path
        if not local_path or not os.path.exists(local_path):
            matched = find_local_pdf_for_document(
                doc_id=document_id,
                original_url=doc.original_pdf_url,
                title=doc.title,
            )
            if matched and matched.exists():
                local_path = str(matched)

        if local_path and os.path.exists(local_path):
            res = ingest_local_pdf(
                local_path=local_path,
                title=doc.title,
                document_id=doc.id,
                case_id=doc.case_id,
                court=doc.court,
                document_type=doc.document_type,
                original_pdf_url=doc.original_pdf_url,
            )
            # Generate summary after re-extraction
            full_text = res.get("full_text", "")
            if full_text:
                generate_document_summary(
                    document_id=document_id,
                    text=full_text,
                    title=doc.title,
                    court=doc.court,
                    document_type=doc.document_type,
                    force_regenerate=True,
                )
            return JSONResponse({"status": "success", "result": res})

        if doc.original_pdf_url:
            res = process_and_ingest_pdf(
                pdf_url=doc.original_pdf_url,
                title=doc.title,
                document_id=doc.id,
                case_id=doc.case_id,
                court=doc.court,
                document_type=doc.document_type,
            )
            full_text = res.get("full_text", "")
            if full_text:
                generate_document_summary(
                    document_id=document_id,
                    text=full_text,
                    title=doc.title,
                    court=doc.court,
                    document_type=doc.document_type,
                    force_regenerate=True,
                )
            return JSONResponse({"status": "success", "result": res})

        raise HTTPException(status_code=400, detail="No source PDF URL or local file available to re-run OCR.")
    finally:
        db.close()


@app.post("/api/admin/extract-all")
async def api_admin_extract_all():
    """
    Batch ingests, extracts OCR & layout, creates separated storage (.txt, .json, RAG chunks),
    and generates AI legal summaries for all PDFs in the repository.
    """
    from app.services.summary_service import batch_extract_and_summarize_all
    stats = batch_extract_and_summarize_all(limit=None, summarize=True)
    return JSONResponse({"status": "success", "stats": stats})


@app.post("/api/documents/{document_id}/summarize")
async def api_document_summarize(document_id: str):
    """
    On-demand AI Legal Summarization endpoint:
    Uses user's local AI model (qwen3:8b via Ollama) to generate a structured 5-part
    executive legal brief.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        text_content = doc.extracted_text or ""
        if not text_content and doc.pages:
            text_content = "\n\n".join(p.page_text or "" for p in doc.pages)
        if not text_content:
            # Check if local PDF exists to extract text first
            matched = find_local_pdf_for_document(
                doc_id=document_id,
                original_url=doc.original_pdf_url,
                title=doc.title,
            )
            if matched and matched.exists():
                res = ingest_local_pdf(
                    local_path=str(matched),
                    title=doc.title,
                    document_id=doc.id,
                    case_id=doc.case_id,
                    court=doc.court,
                    document_type=doc.document_type,
                    original_pdf_url=doc.original_pdf_url,
                )
                text_content = res.get("full_text", "")

        if not text_content:
            text_content = f"Legal Record: {doc.title}. Court: {doc.court or 'Court of Record'}."

        summary_data = generate_document_summary(
            document_id=document_id,
            text=text_content,
            title=doc.title,
            court=doc.court,
            document_type=doc.document_type,
            force_regenerate=True,
        )
        return JSONResponse({"status": "success", "summary": summary_data})
    finally:
        db.close()


@app.post("/api/pipeline/extract-all")
async def api_pipeline_extract_all(limit: int | None = Query(default=None)):
    """
    Batch-extracts and AI-summarizes all PDF documents in data/downloads/ using
    PyMuPDF / Windows Native OCR and the local AI model (qwen3:8b).
    """
    res = batch_extract_and_summarize_all(limit=limit, summarize=True)
    return JSONResponse({"status": "success", "result": res})



# ==========================================
# 4. UNRESTRICTED OPEN DATA & AI ENDPOINTS
# ==========================================

@app.get("/api/open/dump")
async def api_open_dump():
    """
    Full unauthenticated single-payload database dump.
    Returns all cases, documents, court records, and platform statistics in JSON.
    Permits any AI crawler or researcher to ingest the entire database in one call.
    """
    cases = get_all_cases(limit=1000)
    docs = get_all_documents(limit=1000)
    courts = get_all_courts()
    stats = get_platform_statistics()

    return JSONResponse({
        "platform": "CALIP Legal Intelligence Platform",
        "access": "open_unrestricted",
        "documentation": "/llms.txt",
        "full_text_markdown": "/llms-full.txt",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "statistics": stats,
        "cases_count": len(cases),
        "documents_count": len(docs),
        "courts_count": len(courts),
        "cases": cases,
        "documents": docs,
        "courts": courts,
    })


@app.get("/api/open/cases")
async def api_open_cases():
    """Returns all legal cases without authentication for AI agents."""
    cases = get_all_cases(limit=1000)
    return JSONResponse({
        "status": "success",
        "count": len(cases),
        "items": cases,
    })


@app.get("/api/open/documents")
async def api_open_documents():
    """Returns all documents with OCR status and metadata without authentication."""
    docs = get_all_documents(limit=1000)
    return JSONResponse({
        "status": "success",
        "count": len(docs),
        "items": docs,
    })


@app.get("/api/open/ask")
async def api_open_ask(query: str = Query(...)):
    """
    Zero-auth question answering engine for any AI (free Claude, ChatGPT, etc.) or external crawler.
    Returns grounded answers with verbatim page-level legal citations.
    """
    ans = ask_legal_question(query=query)
    return JSONResponse({
        "query": query,
        "answer": ans.get("answer"),
        "confidence": ans.get("confidence", 0.9),
        "sources": ans.get("sources", []),
        "provider": ans.get("provider", "calip-rag-engine"),
    })


@app.get("/api/open/schema")
async def api_open_schema():
    """Returns machine-readable schema for external LLMs to understand the database structure."""
    return JSONResponse({
        "platform": "CALIP Open Legal Schema",
        "version": "1.0",
        "license": "Public Domain / Open Data",
        "entities": {
            "Case": {
                "fields": ["id", "case_number", "title", "court", "bench", "filing_date", "status", "case_type", "case_year", "summary", "subject", "source_url"],
                "relationships": ["documents", "judgments", "orders"],
            },
            "Document": {
                "fields": ["id", "case_id", "title", "document_type", "court", "page_count", "ocr_status", "ocr_confidence", "extraction_method", "file_hash", "original_pdf_url"],
                "relationships": ["pages", "case"],
            },
            "DocumentPage": {
                "fields": ["id", "document_id", "page_number", "page_text", "ocr_confidence", "extraction_method"],
                "relationships": ["document"],
            },
            "Court": {
                "fields": ["id", "name", "court_type", "jurisdiction_state"],
            }
        },
        "endpoints": {
            "llm_manifest": "/llms.txt",
            "llm_full_markdown": "/llms-full.txt",
            "database_dump": "/api/open/dump",
            "open_cases": "/api/open/cases",
            "open_documents": "/api/open/documents",
            "open_ask": "/api/open/ask?query={query}",
            "case_markdown": "/api/cases/{case_id}/markdown",
            "document_markdown": "/api/documents/{document_id}/markdown",
            "document_llm_context": "/api/documents/{document_id}/llm-context",
        }
    })


@app.get("/api/cases/{case_id}/markdown", response_class=PlainTextResponse)
async def api_case_markdown(case_id: str):
    """
    Renders an individual case in clean, pure Markdown for web-browsing AIs (Claude, ChatGPT).
    """
    case = get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case record not found.")

    docs = case.get("documents", [])
    doc_lines = []
    for d in docs:
        doc_lines.append(f"- **[{d.get('title')}]({d.get('url') or '#'})** (ID: `{d.get('id')}`, Pages: {d.get('page_count', 1)}, OCR: {d.get('ocr_status')}) &mdash; [Read Markdown](/api/documents/{d.get('id')}/markdown)")

    md = f"""# CASE RECORD: {case.get('title')}

- **Case Number:** {case.get('case_number')}
- **Court:** {case.get('court') or 'Not Specified'}
- **Bench:** {case.get('bench') or 'Not Specified'}
- **Filing Date:** {case.get('filing_date') or 'Not Specified'}
- **Status:** {case.get('status') or 'Pending'}
- **Case Type:** {case.get('case_type') or 'Civil/Criminal'}
- **Subject / Category:** {case.get('subject') or 'General'}
- **Upstream Source:** {case.get('source_url') or 'N/A'}

## Summary
{case.get('summary') or 'No summary entered.'}

## Attached Legal Documents ({len(docs)})
{chr(10).join(doc_lines) if doc_lines else 'No attached documents.'}

## Machine Citation
```citation
CALIP Case Ref: {case.get('id')} | {case.get('case_number')} | {case.get('court')}
```
"""
    return PlainTextResponse(content=md, media_type="text/markdown; charset=utf-8")


@app.get("/api/documents/{document_id}/markdown", response_class=PlainTextResponse)
async def api_document_markdown(document_id: str):
    """
    Renders an individual document with full extracted OCR text in pure Markdown.
    Can be ingested directly by Claude or ChatGPT when given the URL.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document record not found.")

    ocr_data = get_extracted_ocr_data(document_id)
    full_text = ""
    if ocr_data and ocr_data.get("full_text"):
        full_text = ocr_data["full_text"]
    elif doc.get("extracted_text"):
        full_text = doc["extracted_text"]
    else:
        full_text = "[No text extracted yet. Run OCR extraction at /api/documents/{document_id}/re-extract]"

    md = f"""# LEGAL DOCUMENT: {doc.get('title')}

- **Document ID:** `{doc.get('id')}`
- **Case Reference:** `{doc.get('case_id') or 'Unassigned'}`
- **Court:** {doc.get('court') or 'Not Specified'}
- **Document Type:** {doc.get('document_type') or 'Document'}
- **Total Pages:** {doc.get('page_count', 1)}
- **OCR Status:** {doc.get('ocr_status')}
- **Extraction Method:** {doc.get('extraction_method') or 'Windows Native OCR'}
- **SHA-256 Provenance:** `{doc.get('file_hash') or 'Verified'}`
- **Original PDF URL:** {doc.get('original_pdf_url') or 'Stored locally'}

---
## Verbatim Document Content

```text
{full_text}
```

---
## Citation Metadata
```citation
CALIP Document Ref: {doc.get('id')} | Case: {doc.get('case_id')} | Hash: {doc.get('file_hash')}
```
"""
    return PlainTextResponse(content=md, media_type="text/markdown; charset=utf-8")



@app.get("/health")
async def health_check():
    stats = get_platform_statistics()
    return JSONResponse({
        "status": "healthy",
        "service": "CALIP Legal Intelligence Platform",
        "stats": stats,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    })
