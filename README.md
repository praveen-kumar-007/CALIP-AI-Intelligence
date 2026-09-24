# CALIP

CALIP is a production-oriented legal document intelligence platform for ingesting, structuring, searching, and citing legal records from cases, judgments, orders, applications, and supporting documents.

## Status

This repository is currently being scaffolded. No historic website implementation or production data was present in the workspace, so the project starts from a clean, greenfield state with a migration-safe architecture and a documented audit trail.

## Architecture goals

- Public, SEO-friendly legal pages and canonical URLs
- PDF ingestion with OCR fallback
- Structured legal metadata and entity extraction
- Knowledge graph and vector search
- RAG-driven answer generation with citations
- Read-only public APIs and machine-readable feeds

## Key directories

- app/: application entry points and API routes
- docs/: architecture audit, migration notes, and system design

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Main endpoints

- /
- /cases
- /search
- /api/cases
- /api/search
- /robots.txt
- /sitemap.xml

## Important note

The project preserves a strict source-grounding rule: answers are only supported by document evidence, citations, and provenance metadata where available.
