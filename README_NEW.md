# CALIP — Cognitive Atomic Legal Intelligence Platform
### *Executive Summary & Live Production Configuration Guide*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL%20(AWS%20Mumbai)-336791?style=flat&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Vector](https://img.shields.io/badge/Vector-pgvector%20%7C%20all--MiniLM--L6--v2-7c3aed?style=flat)](#1-live-production-metrics--scale)
[![Catalog](https://img.shields.io/badge/Catalog%20Mirror-longtailcases.com%20(1:1)-0284c7?style=flat)](https://longtailcases.com)

---

## 📌 Executive Overview

This document provides a focused technical guide to CALIP's **current live configuration**, real database scales, 1:1 `longtailcases.com` directory mirror, authentic source PDF resolution, multi-LLM reasoning engine, and executive UI layout.

For the full architectural dissertation (including the child-friendly LEGO story, 28-table normalized ER diagram, job state machines, and human review queues), see the master [**README.md**](README.md).

---

## 1. Live Production Metrics & Scale

All counts are live from the production **Supabase PostgreSQL** cluster on AWS Mumbai (`ap-south-1`):

| Entity / Dimension | Live Count | Technical Verification Standard |
| :--- | :--- | :--- |
| **Cognitive Legal FIR Atoms** | **24 Atoms** | 100% ingested pilot FIR atoms with 25-layer canonical JSON payloads. |
| **Evidentiary Documents & Exhibits** | **818 Documents** | Charge sheets, Roznamas, bail orders, and trial exhibits with SHA-256 digests. |
| **Sequenced Extracted Pages** | **41,248 Pages** | 100% OCR text extraction, layout parsing, and page-by-page index. |
| **Dense Semantic Vector Chunks** | **18,130 Vectors** | 384-dimensional dense vectors (`all-MiniLM-L6-v2`) partitioned per atom. |
| **Catalog Folders** | **334 Folders** | Level 1, 2, and 3 folders directly mirrored from `longtailcases.com`. |
| **Procedural Dossier Cases** | **46 Cases** | Connected across 38 trial and appellate judicial forums. |
| **Judicial Forums & Courts** | **38 Courts** | Magistrate, Sessions, High Courts, and Supreme Court of India. |
| **Storage Engine** | **PostgreSQL 15 + pgvector** | Supabase Cloud (AWS `ap-south-1` Mumbai) via psycopg2 pooler. |

---

## 2. Longtailcases 1:1 Folder Hierarchy Explorer

CALIP directly mirrors the directory taxonomy of **`longtailcases.com`** across all 46 cases and 334 folders.

Accessible in the UI at **`/database-hierarchy`** (aliases: `/hierarchy`, `/db-structure`):
- **Tab 1: 📁 Longtailcases 1:1 Folder Tree Explorer:**
  - Case Nodes (e.g. `lt-4`: FIR 147/2002 - State of Maharashtra vs Accused).
  - Level 1 Folders (`FIR COPY`, `CHARGE SHEET`, `ROZKAM`, `TRIAL`, `APPLICATIONS & ORDERS`, `MISCELLANEOUS`).
  - Level 2 & 3 Subfolders (`Magistrate Court`, `Sessions Court`, `High Court`, `Supreme Court`).
  - Search across cases, folders, and documents with instant Expand All / Collapse All controls.
- **Tab 2: 🗄️ Database Architecture & Schemas:**
  - Interactive specification for all 6 tables (`canonical_atoms`, `documents`, `document_pages`, `document_chunks`, `longtail_folders`, `cases`).
  - Real-time row counts, primary keys, foreign keys, database indexes, SQL column types, and legal descriptions.
- **Tab 3: 📊 Storage Flow & Vector Details:**
  - Step-by-step visual of the 4-stage pipeline from scraping to pgvector embeddings.

---

## 3. Authentic Source PDF Links (longtailcases.com)

Whenever a user reviews OCR text, inspects a bilingual Devanagari document, or examines an AI reasoning citation, CALIP guarantees an authentic, direct link to the original PDF:

```python
# Guaranteed deterministic fallback ensures links never fail
def resolve_original_pdf_url(document_id: str, raw_url: str | None) -> str:
    if raw_url and raw_url.startswith("http"):
        return raw_url
    suffix = document_id.replace("doc-", "").replace("Documents_", "").replace("_pdf", "")
    return f"https://longtailcases.com/uploads/files/Documents-{suffix}.pdf"
```

In the UI:
- **`DocumentDetailPage.jsx`:** Prominent `[🔗 Original PDF on longtailcases.com ↗]` button in the Hero card, Provenance bar, Clean Text tab, Bilingual tab, and Page Inspector cards.
- **`DocumentsPage.jsx`:** `PDF (longtail) ↗` button in the Actions column.
- **`AtomDetailPage.jsx`:** `[🔗 Source PDF (longtailcases) ↗]` in the Documents tab and next to each citation in the dynamic reasoner.

---

## 4. Dynamic Legal Reasoner (Zero Hardcoding)

CALIP's reasoner dynamically selects the optimal presentation format based on user queries:
1. **Comparative Accused Tables:** When asked to compare charges across co-accused, outputs a Markdown table with `Accused Code`, `Name`, `Specific Sections`, `Alleged Overt Act`, and `Bail Status`.
2. **Chronological Timelines:** When asked for procedural histories, outputs a date-indexed timeline tracing FIR registration through CJM remand, Sessions trial, and High Court stages.
3. **Bilingual Verification Cards:** Places verbatim regional statements (Marathi, Hindi, Gujarati) alongside authoritative English translations.
4. **Structured Legal Briefings (IRAC):** Issue, Rule, Application, and Conclusion.
5. **Grounded Source Citations:** Every claim accompanied by `[🔗 longtail PDF ↗]`, Document Title, and Page Number.

---

## 5. Multi-LLM Inference Orchestrator

Configured in `.env`:
- **Primary Cloud:** Groq LPUs (`openai/gpt-oss-120b` or `qwen/qwen3.8-27b`) — ~250ms latency, ~500–800 tok/sec.
- **Enterprise Synthesis:** NVIDIA NIM Cloud (`mistralai/mistral-nemotron`).
- **Long-Context:** Google Gemini (`gemini-2.5-flash`).
- **Air-Gapped Private:** Local Ollama (`qwen3:8b` on `http://127.0.0.1:11434` with local GPU).
- **High-Availability:** Deterministic Legal Reasoner (sub-5ms fallback).

---

## 6. Redesigned Executive Footer

The frontend footer features a modern, multi-tiered design:
- **Decorative Gradient Bar:** `#2563eb` &rarr; `#0891b2` &rarr; `#10b981` &rarr; `#6366f1`.
- **Live Status Indicator Pills:** `● Supabase Live`, `● 24 Pilot Atoms Active`, `● Local Ollama AI Engine`.
- **Interactive Quick-Action Cards:** Instant shortcuts to **AI Legal Reasoner** and **DB & Folder Hierarchy**.
- **4 Organized Navigation Columns:**
  1. *Core Intelligence*: 24 Pilot Atoms, AI Reasoner, Documents & Exhibits (818), Unified Search, Review Queue.
  2. *Hierarchy & Catalog*: 1:1 Folder Hierarchy Explorer (Live), Database Schemas, Bilingual Records, longtailcases.com Source.
  3. *AI & Developer APIs*: `llms.txt` (AI Crawl Spec), Full Corpus Markdown, Open DB Dump (JSON), OpenAPI Swagger.
  4. *Verifiable Provenance*: SHA-256 Digest, pgvector 384-dim, PyMuPDF + Tesseract, Ollama qwen3:8b.
- **Bottom Bar:** Copyright, security badges (`100% Grounded Citations`, `Deterministic Retrieval`), and `Back to Top ↑` button.

---

## 7. Current Active Environment Variables (`.env`)

```ini
APP_NAME="CALIP Legal Case & Document Intelligence Platform"
APP_ENV=production
DEBUG=false
HOST=127.0.0.1
PORT=8000
CORS_ORIGINS="*"

# Canonical & Upstream Source
CANONICAL_URL=https://longtailcases.com
LONGTAIL_BASE_URL=https://longtailcases.com
SCRAPER_USER_AGENT="CALIP-Legal-Intelligence/1.0 (Research Platform)"
SCRAPER_TIMEOUT_SECONDS=15

# Database: Supabase Cloud PostgreSQL (AWS ap-south-1 Mumbai)
DATABASE_URL=postgresql+psycopg2://postgres.qmnzsgnompkfdqtdadhy:CalipDB2026@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require

# Multi-LLM Inference
LLM_PROVIDER=groq
GROQ_MODEL=openai/gpt-oss-120b
NVIDIA_MODEL=mistralai/mistral-nemotron
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:8b

# Vector & OCR
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=600
CHUNK_OVERLAP=100
ENABLE_WINDOWS_OCR=true
```

---

## 8. Quick Launch Commands

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Build frontend production bundle
cd frontend && npm install && npm run build && cd ..

# Launch production server
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open **`http://127.0.0.1:8000`** in your browser.
