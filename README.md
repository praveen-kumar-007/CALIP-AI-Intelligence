# CALIP — Cognitive Atomic Legal Intelligence Platform
### *Enterprise-Grade, Atom-Centric Legal Document Intelligence, Multi-LLM Reasoning & Provenance Verification Engine*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/Database-Supabase%20PostgreSQL%20%7C%20pgvector-336791?style=flat&logo=postgresql&logoColor=white)](https://supabase.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Research-blue.svg)](#license)

---

## 📑 Master Table of Contents

1. [Platform Overview & Executive Summary](#1-platform-overview--executive-summary)
2. [Explain It Like I'm 10: The Intuitive Story](#2-explain-it-like-im-10-the-intuitive-story)
   - [The LEGO Set & Birth Certificate Analogy](#the-lego-set--birth-certificate-analogy)
   - [Visual Journey of a Case (Child-Friendly Flowchart)](#visual-journey-of-a-case-child-friendly-flowchart)
3. [The Core Architectural Philosophy](#3-the-core-architectural-philosophy)
   - [The Fallacy of Case-Centric Indexing](#the-fallacy-of-case-centric-indexing)
   - [The Atomic Directive: One Verified FIR = One Cognitive Atom](#the-atomic-directive-one-verified-fir--one-cognitive-atom)
   - [Multi-Tier Court Progression Hierarchy (Visual Diagram)](#multi-tier-court-progression-hierarchy-visual-diagram)
4. [End-to-End System Topology & Architecture](#4-end-to-end-system-topology--architecture)
   - [Mermaid System Topology Diagram](#mermaid-system-topology-diagram)
   - [Repository Directory Tree](#repository-directory-tree)
   - [Core Pipeline Architecture & Ingestion Flow](#core-pipeline-architecture--ingestion-flow)
5. [Technology Stack & Architectural Rationale](#5-technology-stack--architectural-rationale)
6. [Complete Database Architecture & Schema Specification](#6-complete-database-architecture--schema-specification)
   - [Full Relational Entity-Relationship (ER) Diagram](#full-relational-entity-relationship-er-diagram)
   - [Detailed Table-by-Table Schema Specification](#detailed-table-by-table-schema-specification)
   - [State Machine: Processing Job Lifecycle](#state-machine-processing-job-lifecycle)
   - [State Machine: Atom Hydration Lifecycle](#state-machine-atom-hydration-lifecycle)
   - [The 25-Layer Canonical Cognitive Atom JSON Specification](#the-25-layer-canonical-cognitive-atom-json-specification)
7. [The Multi-LLM Inference Orchestrator](#7-the-multi-llm-inference-orchestrator)
   - [Supported Models & Providers (Groq, NVIDIA NIM, Gemini, Ollama, Deterministic)](#supported-models--providers)
   - [Multi-LLM Fallback & Router Diagram](#multi-llm-fallback--router-diagram)
   - [Grounded Atomic Legal Reasoner (IRAC Methodology)](#grounded-atomic-legal-reasoner-irac-methodology)
   - [RAG Retrieval & Context Sequence Diagram](#rag-retrieval--context-sequence-diagram)
8. [Data Ingestion, Dual OCR & Translation Engine](#8-data-ingestion-dual-ocr--translation-engine)
   - [Dual Extraction Pipeline with Hybrid Fallback](#dual-extraction-pipeline-with-hybrid-fallback)
   - [Vernacular & Bilingual Processing (Marathi, Hindi, Gujarati)](#vernacular--bilingual-processing-marathi-hindi-gujarati)
   - [Document Classification Taxonomy & Regex Markers](#document-classification-taxonomy--regex-markers)
9. [Vector Search, Dense Embeddings & Knowledge Graph](#9-vector-search-dense-embeddings--knowledge-graph)
   - [Dense Vector Indexing & Cosine Distance Engine](#dense-vector-indexing--cosine-distance-engine)
   - [Legal Entity-Relationship Graph & Subgraph Visualization](#legal-entity-relationship-graph--subgraph-visualization)
10. [Frontend Architecture & UI Modules](#10-frontend-architecture--ui-modules)
11. [Exhaustive REST API Reference](#11-exhaustive-rest-api-reference)
12. [Installation, Environment Setup & Deployment](#12-installation-environment-setup--deployment)
    - [Prerequisites](#prerequisites)
    - [Local Development Setup (PowerShell & Bash)](#local-development-setup-powershell--bash)
    - [Docker Deployment with Docker Compose](#docker-deployment-with-docker-compose)
    - [Exhaustive Environment Variable Reference](#exhaustive-environment-variable-reference)
13. [Human-in-the-Loop Review Queue & Provenance Audit](#13-human-in-the-loop-review-queue--provenance-audit)
14. [SEO, Web Crawlers & AI Manifests (llms.txt)](#14-seo-web-crawlers--ai-manifests-llmstxt)
15. [Troubleshooting, Performance Tuning & FAQ](#15-troubleshooting-performance-tuning--faq)
16. [License & Governance](#16-license--governance)

---

## 1. Platform Overview & Executive Summary

**CALIP** (**C**ognitive **A**tomic **L**egal **I**ntelligence **P**latform) is a unified legal document operating system, extraction pipeline, and neural reasoning engine designed to solve the chronic fragmentation of criminal law records.

In traditional legal software, court orders, bail petitions, charge sheets, witness depositions, and High Court appeals are saved as disjointed, isolated PDF files. When lawyers, judges, or researchers ask questions, traditional AI models hallucinate because they lack a single source of truth connecting all these documents.

CALIP introduces an architectural revolution: **One Verified First Information Report (FIR) = One Cognitive Atom**. Every single legal artifact—from initial police custody and forensic seizure memos to High Court bail orders and Supreme Court Special Leave Petitions (SLPs)—is resolved, normalized, and bound to its parent canonical **Atom**. With multi-provider LLM orchestration, verifiable source provenance (exact document ID, page number, and paragraph citation), bilingual OCR extraction, and interactive graph exploration, CALIP turns messy legal archives into deterministic, verifiable intelligence.

---

## 2. Explain It Like I'm 10: The Intuitive Story

### The LEGO Set & Birth Certificate Analogy

Imagine you have a messy toy box with 1,000 mixed-up puzzle pieces and blocks from 50 different LEGO sets. 
- **The Old, Broken Way**: Traditional legal software dumps all 1,000 pieces on the floor and tries to guess which piece fits where. If a lawyer asks, *"Where is the red roof?"*, the computer gets confused because there are 20 different roofs from 20 different sets!
- **CALIP's Smart Way**: CALIP looks for the **Original Instruction Manual (the FIR)** for each LEGO set!

In real life, whenever something serious happens and police investigate, they write down a special document called an **FIR (First Information Report)**. Think of the FIR like a **baby's birth certificate**:
1. You only get **one** birth certificate when you are born.
2. When you start school, graduate college, get a passport, get a driver's license, or win a sports trophy, all those certificates belong to **you**—they do not create a brand new person!
3. In criminal law, the FIR is that birth certificate. Every subsequent court hearing, every bail decision, and every witness statement belongs to that **one original case atom**.

CALIP is like a super-smart detective robot that reads hundreds of crumpled, scanned court papers, finds the matching birth certificates, and puts all related files neatly inside one master superhero binder!

---

### Visual Journey of a Case (Child-Friendly Flowchart)

```mermaid
flowchart TD
    PaperIn["📄 A Legal Paper Arrives\n(Crumpled PDF, Scan, or Order)"] --> SuperScanner["🔍 Super Scanner (OCR Engine)\nReads English, Marathi, Hindi text"]
    SuperScanner --> Question{"❓ What kind of paper is this?"}
    
    Question -->|"It's an FIR!"| CreateAtom["🌱 Birth Certificate Found!\nCreate a New Legal Cognitive Atom"]
    Question -->|"It's a Bail Order or Hearing!"| DetectiveSearch["🔗 Detective Resolver\nFinds which existing Atom it belongs to!"]
    
    CreateAtom --> MasterBinder["📁 Master Case Binder\n(Accused, Charges, Witnesses, Evidence, Timeline)"]
    DetectiveSearch --> MasterBinder
    
    MasterBinder --> SmartBrain["🧠 Multi-LLM Brain (Groq / NVIDIA / Gemini)\nAnalyzes facts using the IRAC Law Method"]
    SmartBrain --> SuperProof["🏆 Super-Proof Answer!\n'Here is the exact truth, and here is Page 4 showing the quote!'"]

    style PaperIn fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style SuperScanner fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#fff
    style Question fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff
    style CreateAtom fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style DetectiveSearch fill:#1e1b4b,stroke:#c084fc,stroke-width:2px,color:#fff
    style MasterBinder fill:#134e4a,stroke:#2dd4bf,stroke-width:2px,color:#fff
    style SmartBrain fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
    style SuperProof fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#fff
```

---

## 3. The Core Architectural Philosophy

### The Fallacy of Case-Centric Indexing

Most legal software catalogs records using **Court Case Numbers** (e.g., *Criminal Bail Application No. 412/2023 at Sessions Court, Pune*). This approach causes systemic failures:
1. **Case Number Multiplicity**: A single criminal matter spawns 5 to 15 different case numbers across Magistrate, Sessions, Special Courts, High Courts, and the Supreme Court. A search for one case number misses 90% of the judicial record.
2. **CNR Desynchronization**: CNR numbers (Case Information System 16-character codes) are assigned per-court and change as cases move across tiers.
3. **Ghost Categories**: Scraping court portals frequently mistakes website headings (e.g., *"Group Orders"*, *"Transfer Petitions"*) for substantive legal cases.

### The Atomic Directive: One Verified FIR = One Cognitive Atom

CALIP enforces a strict rule: **One Verified FIR = One Legal Cognitive Atom**.

```
Canonical FIR Key = [STATE] + [DISTRICT] + [POLICE_STATION] + [FIR_NUMBER] + [FIR_YEAR]
Example: MH-PUNE-SHIVAJINAGAR-0123-2023
```

All other legal events are attached as children of this root node:

```
Canonical Legal Cognitive Atom (e.g., MH-PUNE-SHIVAJINAGAR-0123-2023)
│
├── 📜 1. Core FIR Record (Date, Police Station, Informant, Registered IPC/BNS Sections)
├── ⚖️ 2. Procedural Lineage (Magistrate Remand → Sessions Trial → High Court Bail → SC SLP)
├── 👥 3. People & Roles (Accused A1..An, Complainant, Witnesses PW1..PWn, Investigating Officer)
├── 📑 4. Police Investigation Reports (Panchnama, Seizures, Forensic, Charge Sheet)
├── 📊 5. Accused-Charge-Evidence Matrix (A1 → IPC 420/120B → Overt Act → Ex.P-1 → Status)
├── 💼 6. Evidence Registry (E1..En, Chain of Custody, Hashes, Admissibility)
├── 🎙️ 7. Witness Testimonies (PW Statements, Sec 161/164, Depositions, Contradictions)
├── 🛡️ 8. Bail Chronology (Regular, Anticipatory, Interim, Conditions Imposed)
└── 🔍 9. Verifiable Provenance Ledger (Document ID, Page, Paragraph, Verbatim Quote, SHA-256)
```

---

### Multi-Tier Court Progression Hierarchy (Visual Diagram)

The following diagram illustrates how CALIP tracks a matter as it climbs from local police registration to the Supreme Court of India, preserving continuity under one canonical Atom:

```mermaid
graph TD
    Police["🚔 Police Station\nFIR Registered u/s 154 CrPC\nCanonical Atom Created"] --> MagCourt["⚖️ Tier 1: Magistrate Court (JMFC)\n- Remand & Police Custody\n- Section 167(2) Statutory Bail\n- Section 209 Committal to Sessions"]
    
    MagCourt --> Sessions["🏛️ Tier 2: Court of Sessions / Special Court\n- Framing of Charges (Sec 228 CrPC)\n- Accused Plea & Trial Examination\n- Prosecution Evidence (PW-1..PW-n, Ex.P-1..P-n)\n- Section 313 CrPC Accused Statement\n- Final Judgment: Acquittal or Conviction"]
    
    Sessions --> HighCourt["🏛️ Tier 3: High Court\n- Section 439 CrPC Regular Bail\n- Section 482 CrPC Quashing Petition\n- Criminal Appeal against Conviction\n- Criminal Revision Application"]
    
    HighCourt --> SupremeCourt["🏛️ Tier 4: Supreme Court of India\n- Article 136 Special Leave Petition (SLP)\n- Constitutional Writ Petition\n- Final Appellate Judgment"]

    subgraph AtomWrapper["⚛️ Unified Under One Canonical Legal Cognitive Atom"]
        Police
        MagCourt
        Sessions
        HighCourt
        SupremeCourt
    end

    style AtomWrapper fill:#090d16,stroke:#3b82f6,stroke-width:3px,color:#fff
    style Police fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style MagCourt fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style Sessions fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff
    style HighCourt fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style SupremeCourt fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
```

---

## 4. End-to-End System Topology & Architecture

### Mermaid System Topology Diagram

```mermaid
graph TB
    subgraph ClientLayer["🖥️ Frontend Tier (React 18 + Vite SPA)"]
        UI_Home["🏠 Home & Search Portal"]
        UI_Atom["⚛️ Atom Intelligence Dossier"]
        UI_Doc["📄 Document & OCR Studio"]
        UI_RAG["🧠 AI Research & Reasoner"]
        UI_Admin["🛠️ Admin Pipeline & Review Queue"]
    end

    subgraph APILayer["⚡ Application & Orchestration Tier (FastAPI + Python 3.11+)"]
        API_Gateway["API Router & Middleware\n(CORS, Global Error Handlers, Static Files)"]
        Scraper_Worker["🕷️ Longtail Scraper\n(Recursive Catalog Crawler)"]
        Dropzone_Worker["📥 Incoming Folder Watcher\n(Background Auto-Sync Worker)"]
        Classifier["🏷️ Document Classifier\n(Pattern, Structural, & NLP Scoring)"]
        Resolver["🔗 Atom Resolver\n(State, District, PS, FIR Extraction)"]
        Hydration["💧 Hydration Engine\n(25-Layer Canonical Assembler)"]
        Reasoner["⚖️ Atomic Reasoner\n(IRAC Methodology Context Builder)"]
    end

    subgraph DataEngine["⚙️ Ingestion & Document Processing Engine"]
        PDF_Parser["PyMuPDF (fitz)\nDigital Text & Coordinates"]
        OCR_Engine["Dual OCR Pipeline\n(Windows Native OCR + Tesseract 5.0 + OpenCV)"]
        Translator["🌐 Vernacular Engine\n(Marathi / Hindi / Gujarati → English)"]
        Chunker["✂️ Semantic Chunker\n(600 chars, 100 overlap)"]
    end

    subgraph VectorAndAI["🤖 Cognitive & Retrieval Tier"]
        Embedder["Dense Embedder\n(all-MiniLM-L6-v2, 384-dim)"]
        VectorDB["Cosine Vector Engine\n(pgvector / Normalized In-Memory)"]
        LLM_Router["🔀 Multi-Provider LLM Orchestrator"]
        LLM_Groq["Groq Cloud LPUs\n(Qwen 3.8-27B / Llama 3.3-70B)\n500-800 tps"]
        LLM_Nvidia["NVIDIA NIM\n(Mistral-Nemotron)"]
        LLM_Gemini["Google Gemini API\n(Gemini 2.0 Flash)\n1M Context"]
        LLM_Ollama["Local Ollama GPU\n(Qwen 3:8B / Llama 3:8B)"]
        LLM_Rules["Deterministic Rule Engine\n(Sub-5ms Fallback)"]
    end

    subgraph StorageLayer["💾 Persistence Tier (PostgreSQL + File Vault)"]
        Postgres[("Supabase Cloud PostgreSQL\n- 28 Relational Tables\n- Atoms & Proceedings\n- Provenance Audit Ledger")]
        LocalStore[("Encrypted File Storage\n- Original PDF Documents\n- Extracted JSON OCR Artefacts\n- SHA-256 Checksums")]
    end

    %% Flow Connections
    ClientLayer -->|REST / JSON Requests| APILayer
    Scraper_Worker -->|Raw Legal Files| DataEngine
    Dropzone_Worker -->|Incoming PDFs| DataEngine
    DataEngine -->|Structured Text & Chunks| APILayer
    APILayer -->|Entities & Relations| StorageLayer
    APILayer -->|Chunks & Embeddings| VectorAndAI
    Reasoner -->|Hybrid Retrieval| VectorAndAI
    VectorAndAI -->|Route Prompts| LLM_Router
    LLM_Router --> LLM_Groq
    LLM_Router --> LLM_Nvidia
    LLM_Router --> LLM_Gemini
    LLM_Router --> LLM_Ollama
    LLM_Router --> LLM_Rules
    StorageLayer <-->|Read / Write Transactions| APILayer
```

---

### Repository Directory Tree

```
CALIP-AI-Intelligence/
│
├── .env.example                       # Documented environment configuration template
├── .gitignore                         # Git exclusion rules
├── Dockerfile                         # Multi-stage production container specification
├── docker-compose.yml                 # Orchestration for FastAPI, PostgreSQL & Volumes
├── package.json                       # Root script package definition
├── requirements.txt                   # Production Python backend dependencies
├── requirements-full.txt              # Full ML dependencies (PyTorch, SentenceTransformers)
├── run_app.bat                        # Windows 1-click launch batch script
├── build_frontend.bat                 # Windows frontend build helper
├── vercel.json                        # Serverless edge deployment manifest
│
├── app/                               # FastAPI Application Core
│   ├── __init__.py
│   ├── main.py                        # Unified FastAPI ASGI server & route definitions
│   │
│   ├── core/                          # Core settings & environmental management
│   │   ├── __init__.py
│   │   └── config.py                  # Pydantic BaseSettings configuration object
│   │
│   ├── db/                            # Relational Persistence Layer
│   │   ├── __init__.py
│   │   ├── models.py                  # 28 SQLAlchemy declarative models & relations
│   │   └── session.py                 # Engine pool, SessionLocal & migration hooks
│   │
│   └── services/                      # Modular Business Logic & Cognitive Services
│       ├── __init__.py
│       ├── atom_resolver.py           # FIR coordinate extraction & canonical naming
│       ├── atomic_reasoner.py         # Evidence-grounded IRAC legal reasoning engine
│       ├── auto_sync.py               # Background dropzone & catalog polling worker
│       ├── document_classifier.py     # 16-class legal document classifier (NLP + Regex)
│       ├── graph_service.py           # Entity extraction & relationship graph builder
│       ├── hydration_engine.py        # 25-layer canonical Atom assembler
│       ├── legal_data.py              # Case, court, and document data queries
│       ├── legal_drafter.py           # Procedural legal template & brief generator
│       ├── legal_search_service.py    # Multi-field keyword and catalog search
│       ├── linkage_service.py         # Cross-FIR, parent-child proceeding linker
│       ├── llm_provider.py            # Multi-provider LLM router & fallback orchestrator
│       ├── longtail_scraper.py        # Recursive crawler for upstream court hierarchies
│       ├── markdown_renderer.py       # LLM-ready markdown document generators
│       ├── ocr_service.py             # Dual Windows Native / Tesseract OCR engine
│       ├── pdf_ingest.py              # Cryptographic hashing & PyMuPDF digital parser
│       ├── rag_service.py             # Grounded retrieval-augmented generation engine
│       ├── summary_service.py         # Extractive & abstractive legal summarizers
│       └── vector_service.py          # 384-dim dense vector indexing & cosine search
│
├── frontend/                          # React 18 Single-Page Application (SPA)
│   ├── index.html                     # HTML5 shell with Google Font typography
│   ├── package.json                   # React, Vite, Lucide dependencies
│   ├── vite.config.js                 # Vite bundler & reverse proxy configuration
│   │
│   └── src/
│       ├── main.jsx                   # React root entry point
│       ├── App.jsx                    # Route switch & top-level layout wrapper
│       ├── index.css                  # 46KB+ Handcrafted CSS tokens (dark mode, glass)
│       │
│       ├── components/                # Reusable UI component modules
│       │   ├── atoms/AtomCard.jsx     # Canonical atom preview cards with badge status
│       │   ├── documents/DocCard.jsx  # PDF document preview card with OCR indicators
│       │   ├── search/SearchBar.jsx   # Debounced global search bar with filters
│       │   └── layout/                # Navbars, sidebars, breadcrumbs, footers
│       │
│       ├── context/                   # Global React state contexts
│       ├── services/                  # API client bindings (axios / fetch wrapper)
│       │
│       └── pages/                     # 16 Specialized Screen Views
│           ├── HomePage.jsx           # Global landing page, metrics, jurisdiction map
│           ├── AtomsPage.jsx          # Canonical Atom directory & state filter
│           ├── AtomDetailPage.jsx     # Deep 25-layer Atom dossier with interactive tabs
│           ├── CasesPage.jsx          # Court cases directory
│           ├── CaseDetailPage.jsx     # Case file viewer & procedural timeline
│           ├── DocumentsPage.jsx      # Document vault with OCR status indicators
│           ├── DocumentDetailPage.jsx # Split-screen PDF viewer, OCR text & JSON
│           ├── AIResearchPage.jsx     # Interactive RAG assistant & IRAC reasoner
│           ├── SearchPage.jsx         # Full-text & semantic vector search
│           ├── CourtsPage.jsx         # Comprehensive court directory
│           ├── JudgmentsPage.jsx      # Final judgments & conviction records
│           ├── OrdersPage.jsx         # Interim & bail order records
│           ├── LongtailPage.jsx       # Scraped directory tree explorer
│           ├── ReviewQueuePage.jsx    # Human-in-the-loop audit & approval studio
│           ├── AdminDashboardPage.jsx # Ingestion worker monitor & OCR metrics
│           └── AboutPage.jsx          # System documentation & architectural ethos
│
├── data/                              # Local Storage Repositories (Ignored in Git)
│   ├── downloads/                     # Cached PDF documents
│   ├── incoming/                      # Auto-sync watch dropzone
│   ├── ocr_extracted/                 # Pre-computed OCR JSON artifacts
│   └── calip.db                       # Local SQLite fallback database
│
└── docs/                              # Architectural Reports & Specifications
    ├── CALIP_ATOM_CENTRIC_ARCHITECTURE_REPORT.md
    ├── DATA-MAPPING.md
    ├── DEPLOYMENT_GUIDE.md
    └── LEGAL-AI-ARCHITECTURE.md
```

---

## 5. Technology Stack & Architectural Rationale

| Architectural Tier | Technology / Library | Version | Purpose & Rationale |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** | `>=0.115.0` | Asynchronous ASGI web framework. Native Pydantic validation ensures strict typing, high throughput, and automatic OpenAPI documentation. |
| **Server Runtime** | **Uvicorn** | `>=0.30.0` | High-performance ASGI runtime powered by `uvloop` and `httptools`. |
| **Language Runtime** | **Python** | `3.11 / 3.12 / 3.13` | Modern Python with advanced type hinting, pattern matching, and native async tasks. |
| **Frontend Framework** | **React** | `18.3.1` | Component-driven frontend architecture with concurrent rendering. |
| **Build Bundler** | **Vite** | `5.4.2` | Ultra-fast ESM compilation with instantaneous Hot Module Replacement (HMR). |
| **Client Routing** | **React Router DOM** | `6.26.0` | Declarative client-side routing supporting deep links to individual atoms and documents. |
| **Iconography** | **Lucide React** | `0.441.0` | Crisp, tree-shakable SVG icon suite. |
| **Styling & CSS** | **Vanilla CSS Tokens** | Custom (46KB+) | Pure handcrafted design system with CSS custom properties (`--bg-primary`, `--accent-teal`, glassmorphic backdrops). Zero runtime CSS-in-JS overhead. |
| **Relational Database** | **PostgreSQL (Supabase)** | `15+` | Enterprise ACID relational database hosted on Supabase Cloud with connection pooling and `pgvector` extension. |
| **ORM & Database Driver**| **SQLAlchemy + Psycopg2** | `2.0.32` / `2.9.9` | Declarative relational mapping, transaction safety, and pooling. |
| **Dense Vector Embeddings**| **Sentence-Transformers** | `all-MiniLM-L6-v2` | Generates 384-dimensional dense vectors fine-tuned for semantic retrieval. |
| **Digital PDF Parsing** | **PyMuPDF (`fitz`)** | `>=1.24.10` | High-speed C-native PDF text extraction, boundary box detection, and page rendering. |
| **OCR Engines** | **Windows OCR / Tesseract**| `winocr` / `5.0` | Sub-second native Windows OCR for Windows hosts, with Tesseract 5.0 and OpenCV deskewing for Linux containers. |
| **Primary Cloud LLM** | **Groq Cloud (LPUs)** | `qwen3.8-27b` | Ultra-low latency inference (500–800 tokens/sec) on Groq Language Processing Units. |
| **Secondary Cloud LLMs** | **NVIDIA NIM & Gemini** | `mistral-nemotron` / `gemini-2.0` | High-capacity reasoning models with context windows up to 1M tokens. |
| **Local Private LLM** | **Ollama** | `qwen3:8b` / `llama3:8b` | 100% private, offline inference on local consumer GPUs. |
| **Fallback Engine** | **Deterministic Parser** | Native Python | Zero-dependency, sub-5ms rule engine ensuring 100% platform uptime even without external internet connectivity. |

---

## 6. Complete Database Architecture & Schema Specification

CALIP features a normalized, 28-table relational data model that maps every legal entity with precision.

### Full Relational Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    COURTS ||--o{ CASES : "adjudicates"
    CASES ||--o{ DOCUMENTS : "owns"
    CASES ||--o{ LONGTAIL_FOLDERS : "contains"
    
    ATOMS ||--o{ ATOM_PROCEEDINGS : "progresses through"
    ATOMS ||--o{ ATOM_ACCUSED : "charges"
    ATOMS ||--o{ ATOM_EVIDENCE : "indexes"
    ATOMS ||--o{ ATOM_WITNESSES : "examines"
    ATOMS ||--o{ ATOM_BAIL_RECORDS : "tracks"
    ATOMS ||--o{ ATOM_ALLEGATIONS : "records"
    ATOMS ||--o{ ATOM_PROVENANCE : "grounds"
    ATOMS ||--o{ ATOM_LINKS : "associates"
    ATOMS ||--o{ DOCUMENTS : "aggregates"
    
    ATOM_ACCUSED ||--o{ ATOM_ACCUSED_CHARGES : "faces"
    ATOM_ACCUSED ||--o{ ATOM_BAIL_RECORDS : "applies for"
    
    DOCUMENTS ||--o{ DOCUMENT_PAGES : "divided into"
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "partitioned into"
    DOCUMENTS ||--o{ ATOM_PROVENANCE : "cites"
    DOCUMENTS ||--o{ ATOM_REVIEW_QUEUE : "flags"
    
    ACTS ||--o{ SECTIONS : "contains"
    LEGAL_ENTITIES ||--o{ RELATIONSHIP_EDGES : "relates"

    ATOMS {
        string id PK "UUID"
        string canonical_fir_id UK "MH-PUNE-SHIVAJINAGAR-0123-2023"
        string state "Indexed"
        string district "Indexed"
        string police_station "Indexed"
        string fir_number "Indexed"
        int fir_year "Indexed"
        string registration_date
        string complainant_name
        string sections_registered
        string original_language "Marathi / Hindi / English"
        boolean zero_fir "True if transferred"
        string cross_fir_id "Link to cross-matter"
        string hydration_status "DISCOVERED | PARTIAL | HYDRATED | VERIFIED"
        float confidence_score "0.0 - 1.0"
        boolean is_verified "Human audited flag"
    }

    ATOM_PROCEEDINGS {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string court_tier "MAGISTRATE | SESSIONS | HIGH_COURT | SUPREME_COURT"
        string court_name
        string case_number "Indexed"
        string cnr "16-char CIS Code"
        string presiding_judge
        string status "PENDING | DISPOSED"
        string filing_date
        string disposal_date
    }

    ATOM_ACCUSED {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string accused_code "A1, A2, A3"
        string canonical_name "Standardized name"
        json aliases "List of alias strings"
        string custody_status "IN_CUSTODY | BAIL_GRANTED | ABSCONDING"
        int custody_days "Cumulative days in detention"
    }

    ATOM_ACCUSED_CHARGES {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string accused_id FK "References atom_accused.id"
        string statute "Indian Penal Code / BNS"
        string section "e.g. 420, 409, 120B"
        text overt_act_allegation "Specific factual overt act"
        string charge_stage "FIR | CHARGE_SHEET | FRAMED | CONVICTED"
        string trial_outcome "PENDING | ACQUITTED | CONVICTED"
    }

    ATOM_EVIDENCE {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string evidence_code "E1, E2"
        string category "DOCUMENTARY | DIGITAL | FORENSIC | MATERIAL"
        string title "Title of Exhibit"
        string exhibit_number "Ex.P-1, Ex.D-1"
        string custodian "Current custody holder"
        string source_document_id FK "References documents.id"
        int page_number "Page reference"
        string admissibility_status "ADMISSIBLE | DISPUTED"
        text proves_proposition "Factual proposition proved"
    }

    ATOM_WITNESSES {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string witness_code "PW-1, PW-2, DW-1"
        string witness_name
        string witness_role "EYEWITNESS | PANCH | INVESTIGATING_OFFICER"
        text statement_161_summary "Police statement summary"
        text deposition_summary "Courtroom cross-examination summary"
        boolean is_hostile "Flagged if hostile"
    }

    ATOM_BAIL_RECORDS {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string accused_id FK "References atom_accused.id"
        string bail_type "REGULAR | ANTICIPATORY | DEFAULT | INTERIM"
        string application_date
        string decision_date
        string outcome "GRANTED | REJECTED | WITHDRAWN"
        text grounds_urged "Defense arguments"
        text prosecution_objections "State objections"
        text conditions_imposed "Bail conditions (surety, passport deposit)"
    }

    ATOM_PROVENANCE {
        string id PK "UUID"
        string atom_id FK "References atoms.id"
        string target_table "Table name"
        string target_id "Record ID"
        string target_field "Column name"
        string source_document_id FK "References documents.id"
        int page_number "Exact PDF page"
        int paragraph_number "Paragraph number"
        text verbatim_quote "Direct unedited text excerpt"
        float confidence_score "Extraction reliability"
        boolean is_human_verified "Clerk verified"
    }

    DOCUMENTS {
        string id PK "UUID"
        string case_id FK "References cases.id"
        string atom_id FK "References atoms.id"
        string document_type "FIR | ChargeSheet | Roznama | Order | Judgment"
        string title
        string file_hash "SHA-256 Digest"
        int page_count
        string ocr_status "completed | pending | failed"
        text extracted_text
        text original_language_text "Original Marathi/Hindi script"
        text english_translated_text "Verified English draft"
        string detected_language "English | Marathi | Hindi"
    }

    DOCUMENT_CHUNKS {
        string id PK "UUID"
        string document_id FK "References documents.id"
        int page_number
        int chunk_index
        text chunk_text
        int token_count
        json embedding "384-dimensional dense vector"
    }
```

---

### Detailed Table-by-Table Schema Specification

#### 1. Core Platform & Legacy Hierarchy Tables
- **`courts`**: Directory of judicial institutions (`id`, `name`, `court_type`, `jurisdiction`, `state`, `city`).
- **`cases`**: Top-level case matters (`id`, `case_number`, `case_type`, `case_year`, `title`, `court_name`, `bench`, `filing_date`, `status`, `petitioner`, `respondent`, `advocates`, `judges`, `acts`, `sections`, `canonical_url`).
- **`longtail_folders`**: Hierarchical directory structure scraped from upstream legal portals (`id`, `case_id`, `parent_id`, `title`, `folder_type`, `level`, `source_url`).
- **`documents`**: Central document registry with SHA-256 checksums, page counts, OCR status, and bilingual text fields.
- **`document_pages`**: Page-level extraction ledger storing individual page text, image flags, and OCR quality metrics.
- **`document_chunks`**: Segmented text chunks (600 characters, 100 overlap) storing 384-dimensional vector embeddings.
- **`judgments`**: Specialized final rulings storing court, bench, issues, arguments, findings, reasoning, decision, and precedents.
- **`orders`**: Daily and interim court orders (`order_date`, `court`, `bench`, `order_type`, `directions`).
- **`applications`**: Procedural applications filed by litigants (`application_type`, `applicant`, `prayer`, `status`).
- **`acts` & `sections`**: Normalized statutory references (e.g., IPC 1860, CrPC 1973, BNS 2023, BNSS 2023).
- **`legal_entities` & `relationship_edges`**: Knowledge graph nodes (Court, Judge, Advocate, Party, Act) and directed edges (`filed_in`, `has_judge`, `cites`).
- **`processing_jobs`**: Asynchronous pipeline job tracker for document ingestion, OCR, and vectorization.

#### 2. Canonical Atomic Intelligence Tables
- **`atoms`**: The root cognitive entity representing one verified criminal matter (`canonical_fir_id`, `state`, `district`, `police_station`, `fir_number`, `fir_year`, `sections_registered`, `hydration_status`, `confidence_score`, `is_verified`).
- **`atom_proceedings`**: Cross-tier court lineage tracking the atom from Magistrate to Supreme Court with CNR numbers.
- **`atom_accused`**: Roster of accused individuals (`accused_code` A1..An, `canonical_name`, `aliases`, `custody_status`, `custody_days`).
- **`atom_accused_charges`**: Granular statutory charge mapping connecting individual accused to overt acts and stages.
- **`atom_evidence`**: Comprehensive exhibit and physical evidence registry (`evidence_code`, `category`, `exhibit_number`, `custodian`, `admissibility_status`).
- **`atom_witnesses`**: Testimony and deposition records (`witness_code` PW-1..PW-n, `witness_role`, `statement_161_summary`, `deposition_summary`, `is_hostile`).
- **`atom_bail_records`**: Chronological bail history (`bail_type`, `application_date`, `decision_date`, `outcome`, `conditions_imposed`).
- **`atom_allegations`**: Verbatim quotes of factual allegations from informants, victims, and witnesses.
- **`atom_provenance`**: The anti-hallucination audit ledger tying every database fact to an exact document ID, page, paragraph, and verbatim quote.
- **`atom_review_queue`**: Disputed, unverified, or low-confidence records routed for human clerk adjudication.
- **`atom_links`**: Bidirectional relations between companion, cross, or counter-FIR atoms (`same_transaction`, `cross_fir`).

---

### State Machine: Processing Job Lifecycle

Every document processed by CALIP advances through a strict state machine tracked in `processing_jobs`:

```mermaid
stateDiagram-v2
    [*] --> QUEUED: File Uploaded / Scraped
    QUEUED --> DOWNLOADING: Worker Claims Job
    DOWNLOADING --> EXTRACTING: SHA-256 Verified
    EXTRACTING --> OCR: Scanned PDF Detected (<50 chars text)
    EXTRACTING --> CHUNKING: Digital Text Extracted
    OCR --> CHUNKING: OCR Completed with Confidence > 0.60
    OCR --> FAILED: OCR Failed / Unreadable Image
    CHUNKING --> EMBEDDING: Segmented into 600-char Chunks
    EMBEDDING --> GRAPH_UPDATE: Vectors Generated (384-dim)
    GRAPH_UPDATE --> PUBLISHED: Entities & Relations Stored
    PUBLISHED --> [*]
    FAILED --> [*]

    note right of OCR
        Windows Native OCR (winocr)
        or Tesseract 5.0 + OpenCV
    end note

    note right of EMBEDDING
        all-MiniLM-L6-v2 Dense Embedder
    end note
```

---

### State Machine: Atom Hydration Lifecycle

As documents are classified and linked to an Atom, the Atom's `hydration_status` transitions across four lifecycle states:

```mermaid
stateDiagram-v2
    [*] --> DISCOVERED: Initial FIR Reference Found in Document
    DISCOVERED --> PARTIAL: Core Police Station & Accused Identified
    PARTIAL --> HYDRATED: Procedural Lineage, Charges & Evidence Linked
    HYDRATED --> VERIFIED: Reviewed and Approved in Human Review Queue
    
    PARTIAL --> DISPUTED: Conflicting Police Station or Sections Found
    DISPUTED --> VERIFIED: Resolved by Clerk in Review Studio
    VERIFIED --> [*]

    note right of DISCOVERED
        Canonical ID Generated:
        e.g. MH-PUNE-SHIVAJINAGAR-0123-2023
    end note

    note right of VERIFIED
        All Facts Backed by Verified
        Provenance Citations
    end note
```

---

### The 25-Layer Canonical Cognitive Atom JSON Specification

When querying an Atom via `/api/atoms/{atom_id}`, CALIP synthesizes the 28 normalized tables into a structured **25-Layer Canonical JSON Schema**:

```json
{
  "layer_01_canonical_identity": {
    "atom_id": "8fa21c56-324b-4b19-97ec-9801dbf6c21e",
    "canonical_fir_id": "MH-PUNE-SHIVAJINAGAR-0123-2023",
    "state": "Maharashtra",
    "district": "Pune",
    "police_station": "Shivajinagar",
    "fir_number": "123",
    "fir_year": 2023
  },
  "layer_02_jurisdiction": {
    "court_of_first_instance": "Court of Judicial Magistrate First Class, Pune",
    "sessions_division": "Pune Sessions Division",
    "appellate_high_court": "High Court of Judicature at Bombay"
  },
  "layer_03_temporal_timeline": {
    "date_of_occurrence": "2023-04-12",
    "fir_registration_date": "2023-04-13",
    "first_remand_date": "2023-04-14",
    "charge_sheet_filing_date": "2023-07-10"
  },
  "layer_04_complainant_informant": {
    "name": "Ramesh Kumar Joshi",
    "role": "Branch Manager",
    "informant_statement_summary": "Discovered fraudulent loan documents submitted on 12-04-2023."
  },
  "layer_05_accused_roster": [
    {
      "accused_code": "A1",
      "canonical_name": "Suresh Manohar Patil",
      "aliases": ["Surya", "Patil Kaka"],
      "custody_status": "BAIL_GRANTED",
      "custody_days": 84
    },
    {
      "accused_code": "A2",
      "canonical_name": "Vikram Devendra Shah",
      "aliases": ["Vicky"],
      "custody_status": "IN_CUSTODY",
      "custody_days": 172
    }
  ],
  "layer_06_statutory_charges_matrix": [
    {
      "accused_code": "A1",
      "statute": "Indian Penal Code",
      "section": "420",
      "overt_act_allegation": "Forged signature on collateral valuation certificate.",
      "charge_stage": "CHARGES_FRAMED",
      "trial_outcome": "PENDING"
    },
    {
      "accused_code": "A1",
      "statute": "Indian Penal Code",
      "section": "120B",
      "overt_act_allegation": "Criminal conspiracy with A2 to divert disbursed loan funds.",
      "charge_stage": "CHARGES_FRAMED",
      "trial_outcome": "PENDING"
    }
  ],
  "layer_07_procedural_court_lineage": [
    {
      "court_tier": "MAGISTRATE",
      "court_name": "JMFC Pune",
      "case_number": "RCC/412/2023",
      "cnr": "MHPU02004122023",
      "status": "COMMITTED"
    },
    {
      "court_tier": "SESSIONS",
      "court_name": "Sessions Court, Pune",
      "case_number": "Sessions Case 91/2023",
      "status": "PENDING"
    },
    {
      "court_tier": "HIGH_COURT",
      "court_name": "Bombay High Court",
      "case_number": "Criminal Bail Application 1412/2023",
      "status": "DISPOSED"
    }
  ],
  "layer_08_evidence_registry": [
    {
      "evidence_code": "E1",
      "category": "DOCUMENTARY",
      "title": "Forged Title Deed of Flat 402",
      "exhibit_number": "Ex.P-1",
      "admissibility_status": "ADMISSIBLE"
    },
    {
      "evidence_code": "E2",
      "category": "FORENSIC",
      "title": "State Forensic Laboratory Handwriting Analysis",
      "exhibit_number": "Ex.P-2",
      "admissibility_status": "ADMISSIBLE"
    }
  ],
  "layer_09_witness_examinations": [
    {
      "witness_code": "PW-1",
      "witness_name": "Ramesh Kumar Joshi",
      "witness_role": "INFORMANT",
      "statement_161_summary": "Affirmed identification of A1 during loan processing.",
      "is_hostile": false
    },
    {
      "witness_code": "PW-2",
      "witness_name": "Mahesh V. Shinde",
      "witness_role": "PANCH_WITNESS",
      "statement_161_summary": "Witnessed seizure of stamp paper from A1's residence.",
      "is_hostile": false
    }
  ],
  "layer_10_bail_history": [
    {
      "accused_code": "A1",
      "bail_type": "REGULAR",
      "court_tier": "HIGH_COURT",
      "decision_date": "2023-09-18",
      "outcome": "GRANTED",
      "grounds_urged": "Investigation complete, charge sheet filed, parity with co-accused.",
      "conditions_imposed": "Deposit passport, mark presence at PS every Monday."
    }
  ],
  "layer_11_verbatim_allegations": [ ... ],
  "layer_12_provenance_citations": [
    {
      "target_field": "layer_05_accused_roster[0].canonical_name",
      "source_document_id": "doc_99b3b879_fir",
      "page_number": 2,
      "paragraph_number": 3,
      "verbatim_quote": "Accused No. 1 Suresh Manohar Patil, resident of Shivajinagar...",
      "confidence_score": 1.0,
      "is_human_verified": true
    }
  ],
  "layer_13_through_25_extended_attributes": { ... }
}
```

---

## 7. The Multi-LLM Inference Orchestrator

### Supported Models & Providers

CALIP features a pluggable, high-performance LLM orchestrator (`app/services/llm_provider.py`) with zero-downtime automatic fallback across five tiers:

| Provider | Supported Models | Ingestion Speed | Context Window | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Groq Cloud (Default)**| `qwen/qwen3.8-27b`, `llama-3.3-70b-versatile` | **500–800 tokens/sec** | 128,000 tokens | Real-time interactive lawyer chat, instant IRAC legal reasoning. |
| **NVIDIA NIM** | `mistralai/mistral-nemotron`, `meta/llama-3.1-70b` | **120–250 tokens/sec** | 64,000 tokens | Deep cross-jurisdiction statutory synthesis and complex appellate drafting. |
| **Google Gemini** | `gemini-2.0-flash`, `gemini-1.5-pro` | **150–300 tokens/sec** | **1,000,000 tokens** | Massive 100+ page full case file synthesis in a single prompt. |
| **Local Ollama** | `qwen3:8b`, `llama3:8b`, `mistral:7b` | **30–90 tokens/sec** | 32,000 tokens | 100% private, on-premises offline GPU inference for confidential defense cases. |
| **Deterministic Engine**| Pure Python Regex & AST Rules | **Sub-5 milliseconds** | Unlimited | Zero-dependency, offline keyword and regex extraction guaranteeing 100% platform uptime. |

---

### Multi-LLM Fallback & Router Diagram

```mermaid
flowchart TD
    Prompt["Incoming Legal Prompt & Verified Context"] --> Router{"LLM Provider Router\n(Checks Settings & Keys)"}
    
    Router -->|"LLM_PROVIDER=groq"| Groq["🚀 Groq Cloud LPUs\n(Qwen 3.8-27B / Llama 3.3-70B)\nLatency: ~200ms | 500-800 tps"]
    Router -->|"LLM_PROVIDER=nvidia"| Nvidia["⚡ NVIDIA NIM\n(Mistral-Nemotron)\nEnterprise Legal Synthesis"]
    Router -->|"LLM_PROVIDER=gemini"| Gemini["🌌 Google Gemini API\n(Gemini 2.0 Flash)\n1M Token Context Window"]
    Router -->|"LLM_PROVIDER=ollama"| Ollama["🔒 Local Ollama GPU\n(Qwen 3:8B / Llama 3:8B)\n100% Private Offline Engine"]
    
    Groq -->|If Rate-Limited or 5xx| FallbackChain{"Automatic Fallback\nChain"}
    Nvidia -->|If Credits Exhausted| FallbackChain
    Gemini -->|If Network Timeout| FallbackChain
    
    FallbackChain --> Nvidia
    FallbackChain --> Groq
    FallbackChain --> Gemini
    FallbackChain --> Deterministic["🛡️ Deterministic Legal Engine\n(Sub-5ms, Zero Dependencies, 100% Uptime)"]

    style Groq fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style Nvidia fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style Gemini fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff
    style Ollama fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
    style Deterministic fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
```

---

### Grounded Atomic Legal Reasoner (IRAC Methodology)

Lawyers and judicial officers do not accept unstructured generative summaries. CALIP implements the **IRAC Legal Reasoning Methodology**:

1. **Issue (I)**: The precise legal controversy framed with respect to specific accused parties and statutory sections.
2. **Rule (R)**: Applicable provisions of penal statutes (IPC, CrPC, BNS, BNSS) and binding Supreme Court/High Court judicial ratios.
3. **Application (A)**: Factual synthesis matching verified evidence (Exhibits, Panchnamas, 161 Statements) directly against the statutory ingredients of the alleged offense.
4. **Conclusion (C)**: Determinative legal finding or current procedural posture.
5. **Provenance Citations**: An unbroken table verifying every single assertion with Document Title, ID, Page Number, and Verbatim Excerpt.

---

### RAG Retrieval & Context Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as ⚖️ Legal Researcher / Lawyer
    participant UI as 🖥️ React SPA (/ai-research)
    participant API as ⚡ FastAPI (/api/reason)
    participant Reasoner as 🧠 Atomic Reasoner
    participant Resolver as 🔗 Atom Resolver
    participant VectorDB as 🔎 Vector Engine (pgvector)
    participant DB as 💾 Relational DB (Supabase)
    participant LLM as 🤖 Active LLM Provider (Groq/NVIDIA)

    User->>UI: Enter query: "Has A1 filed for regular bail?"
    UI->>API: POST /api/reason { question, canonical_fir_id }
    API->>Reasoner: query_atomic_reasoner(question, atom_id)
    Reasoner->>Resolver: Resolve Canonical Atom Coordinates
    Resolver->>DB: Fetch Atom, Accused, Charges, Bail Records
    DB-->>Reasoner: Return Normalized Structured Relational State
    Reasoner->>VectorDB: Cosine search(query_vector, top_k=5, atom_id)
    VectorDB-->>Reasoner: Return verbatim matching document chunks
    Reasoner->>Reasoner: Assemble Grounded IRAC Prompt & Provenance Context
    Reasoner->>LLM: Dispatch structured prompt with source boundaries
    LLM-->>Reasoner: Generate evidence-grounded IRAC response
    Reasoner->>Reasoner: Verify returned citations against Document IDs
    Reasoner-->>API: Return Answer + Structured Provenance Ledger
    API-->>UI: Return JSON Response
    UI-->>User: Render formatted legal brief with clickable page links
```

---

## 8. Data Ingestion, Dual OCR & Translation Engine

### Dual Extraction Pipeline with Hybrid Fallback

```mermaid
flowchart TD
    FileIn["Incoming Legal File\n(Upload, Scraper, or Dropzone)"] --> Hash["Compute SHA-256 Checksum\nCheck Database for Duplicates"]
    Hash --> Format{"Format Check"}
    
    Format -->|"Digital PDF"| PyMuPDF["PyMuPDF (fitz)\nDirect Text Stream & Coordinate Extraction"]
    Format -->|"Scanned / Image PDF"| OCRRouter{"Check Operating Environment"}
    
    PyMuPDF --> CheckText{"Extracted Text > 50 characters?"}
    CheckText -->|"Yes"| ExtractSuccess["Digital Extraction Succeeded"]
    CheckText -->|"No (Scanned Images)"| OCRRouter
    
    OCRRouter -->|"Windows Host (settings.ENABLE_WINDOWS_OCR)"| WinOCR["⚡ Windows Native OCR (winocr)\nDirect Hardware Accelerated Extraction"]
    OCRRouter -->|"Linux Container / Cloud"| Tesseract["Tesseract OCR 5.0\n+ OpenCV Deskew & Adaptive Thresholding"]
    
    WinOCR --> QualityCheck{"Confidence Score > 0.60?"}
    Tesseract --> QualityCheck
    
    QualityCheck -->|"Yes"| LangDetect["🌐 Language Detection Engine"]
    QualityCheck -->|"No"| FlagQueue["⚠️ Route to Human Review Queue\n(/admin/review-queue)"]
    ExtractSuccess --> LangDetect
    
    LangDetect --> Vernacular{"Detected Language?"}
    Vernacular -->|"Marathi / Hindi / Gujarati"| Translate["Bilingual Engine\nPreserve Vernacular + English Legal Translation"]
    Vernacular -->|"English"| StoreReady["Ready for Storage & Vector Indexing"]
    Translate --> StoreReady
    StoreReady --> SaveDB[("Save to documents & document_pages")]

    style WinOCR fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style Tesseract fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style FlagQueue fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
    style Translate fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff
```

---

### Vernacular & Bilingual Processing (Marathi, Hindi, Gujarati)

Indian state courts frequently register FIRs and Panchnamas in regional languages. CALIP's bilingual engine:
1. **Preserves Native Vernacular**: Verbatim Devanagari (Marathi, Hindi) or Gujarati scripts are preserved in `original_language_text`.
2. **Generates Authoritative English Drafts**: Clean legal English translations are stored in `english_translated_text`.
3. **Dual Indexing**: Both texts are partitioned into chunks and vector-indexed simultaneously. A lawyer can search in English (*"cheating loan agreement"*) and match an FIR registered in Marathi (*"फसवणूक करून कर्ज काढले"*).

---

### Document Classification Taxonomy & Regex Markers

CALIP classifies incoming files into 16 distinct statutory document classes:

| Class Code | Statutory Classification | Key Structural & Regex Markers |
| :--- | :--- | :--- |
| `FIR` | First Information Report | `first information report`, `form no. 24.5(1)`, `u/s 154 cr.p.c`, `prathama khabar` |
| `COMPLAINT` | Written / Private Complaint | `written complaint`, `complaint u/s 156(3)`, `complaint u/s 200 crpc` |
| `CHARGE_SHEET` | Final Police Report u/s 173 | `charge sheet`, `final report u/s 173`, `form no. 5.3`, `doshrop patra` |
| `SUPP_CHARGE_SHEET`| Supplementary Police Report | `supplementary charge sheet`, `further report u/s 173(8)`, `puravni doshrop` |
| `BAIL_APPLICATION` | Bail Application | `application u/s 439`, `anticipatory bail u/s 438`, `default bail 167(2)` |
| `BAIL_ORDER` | Bail Decision / Order | `bail granted`, `bail rejected`, `released on bail`, `furnishing PR bond` |
| `DEPOSITION` | Witness Deposition | `deposition of pw-`, `sworn statement`, `cross examination by advocate` |
| `PANCHNAMA` | Spot / Seizure Memo | `panchnama`, `seizure memo`, `in presence of panchas`, `panch witnesses` |
| `FORENSIC_REPORT` | Scientific / Medical Report | `forensic science laboratory`, `chemical analyzer`, `post-mortem report` |
| `ROZNAMA` | Daily Court Order Sheet | `roznama`, `daily order sheet`, `proceedings of the court`, `adjourned to` |
| `JUDGMENT` | Final Judicial Verdict | `judgment`, `operative order`, `acquitted of charges`, `convicted under section` |
| `ORDER` | Procedural / Interim Order | `interim order`, `summons issued`, `warrant of arrest`, `charges framed` |
| `WRIT_PETITION` | High Court Writ / Revision | `writ petition (crl)`, `criminal revision application`, `petition u/s 482` |

---

## 9. Vector Search, Dense Embeddings & Knowledge Graph

### Dense Vector Indexing & Cosine Distance Engine

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` generating normalized 384-dimensional dense vectors.
- **Chunking Parameters**: Text is segmented into 600-character windows with a 100-character sliding overlap.
- **Cosine Distance Formulation**:
$$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
- **Fallback Serverless Vector Engine**: For lightweight environments (e.g., Vercel / AWS Lambda 250MB size restrictions where PyTorch cannot be installed), CALIP includes an automatic zero-dependency in-memory cosine engine that operates directly on pre-computed float vectors stored in PostgreSQL.

---

### Legal Entity-Relationship Graph & Subgraph Visualization

```mermaid
graph LR
    subgraph CaseEntities["Legal Cognitive Atom Subgraph"]
        Atom["⚛️ Atom: MH-PUNE-SHIVAJINAGAR-0123-2023"]
        A1["👤 Accused A1: Suresh Patil"]
        A2["👤 Accused A2: Vikram Shah"]
        Sec420["📜 Statute: IPC Section 420 (Cheating)"]
        Sec120B["📜 Statute: IPC Section 120B (Conspiracy)"]
        ExP1["💼 Exhibit Ex.P-1: Forged Title Deed"]
        PW1["🎙️ Witness PW-1: Ramesh Joshi (Bank Mgr)"]
        Judge["⚖️ Judge: Hon. V. M. Deshmukh"]
        Sessions["🏛️ Court: Sessions Court, Pune"]
    end

    Atom -->|charges| A1
    Atom -->|charges| A2
    A1 -->|indicted_under| Sec420
    A1 -->|indicted_under| Sec120B
    A2 -->|indicted_under| Sec120B
    ExP1 -->|proves_charge_against| A1
    PW1 -->|testifies_against| A1
    Sessions -->|adjudicates| Atom
    Judge -->|presides_over| Sessions

    style Atom fill:#0f172a,stroke:#38bdf8,stroke-width:3px,color:#fff
    style A1 fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style A2 fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style Sec420 fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style Sec120B fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style ExP1 fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
    style PW1 fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff
    style Sessions fill:#134e4a,stroke:#2dd4bf,stroke-width:2px,color:#fff
```

---

## 10. Frontend Architecture & UI Modules

The frontend is a modern single-page application built with **React 18**, **Vite 5**, and a handcrafted design system in `frontend/src/index.css`.

### Key UI Pages & Functionality

1. **`HomePage.jsx`**: Platform overview, live ingestion metrics, jurisdiction statistics, and universal search bar.
2. **`AtomsPage.jsx`**: The Canonical Atom catalog with filters by State, District, Year, and Hydration status (`HYDRATED`, `VERIFIED`).
3. **`AtomDetailPage.jsx`**: Comprehensive 25-layer dossier displaying accused profiles, charge matrices, court lineages, witness summaries, and provenance badges.
4. **`DocumentsPage.jsx` & `DocumentDetailPage.jsx`**: High-density document repository with split-screen PDF preview, OCR text viewers, and downloadable RAG JSON artifacts.
5. **`AIResearchPage.jsx`**: Grounded legal conversational assistant with model selector (Groq, NVIDIA, Gemini, Ollama) and citations.
6. **`SearchPage.jsx`**: Dual full-text keyword search and semantic vector similarity search.
7. **`ReviewQueuePage.jsx`**: Side-by-side human audit interface displaying raw scanned PDFs alongside extracted JSON fields for clerk verification.
8. **`AdminDashboardPage.jsx`**: Live system health monitor, background worker status, and OCR performance metrics.

---

## 11. Exhaustive REST API Reference

All API routes return uniform JSON payloads with standard HTTP status codes.

### 1. Canonical Atom Endpoints
- `GET /api/atoms` — List all canonical atoms with pagination (`limit`, `offset`, `state`).
- `GET /api/atoms/{atom_id}` — Retrieve full 25-layer canonical JSON for an atom.
- `GET /api/atoms/{atom_id}/documents` — Retrieve all PDF filings belonging to an atom.
- `GET /api/atoms/{atom_id}/hydration` — Retrieve completion scores and missing field metrics.
- `POST /api/reason` — Execute grounded IRAC reasoning bounded to an atom.
  ```json
  // Request Body
  {
    "question": "What overt act is alleged against Accused A1?",
    "canonical_fir_id": "MH-PUNE-SHIVAJINAGAR-0123-2023"
  }
  ```

### 2. Cases, Judgments & Orders
- `GET /api/cases` — Retrieve cases with pagination and search parameters.
- `GET /api/cases/{case_id}` — Retrieve case detail, parties, and filings.
- `GET /api/cases/{case_id}/markdown` — Stream LLM-ready markdown summary of the case.
- `GET /api/cases/{case_id}/linkages` — Retrieve parent, child, and companion case linkages.
- `GET /api/judgments` — Browse judgments and trial verdicts.
- `GET /api/orders` — Browse interim and bail orders.
- `GET /api/courts` — Directory of courts across judicial tiers.

### 3. Document Processing & OCR
- `GET /api/documents/{document_id}` — Retrieve document metadata and OCR status.
- `GET /documents/{document_id}/view/txt` — View extracted verbatim text in browser.
- `GET /documents/{document_id}/download/txt` — Download extracted `.txt` file.
- `GET /documents/{document_id}/download/json` — Download page-by-page RAG JSON artifact.
- `GET /download/{document_id}` — Download original PDF file.
- `POST /api/upload` — Multipart file upload triggering SHA-256 deduplication and OCR.

### 4. Admin & Verification
- `GET /api/review-queue` — List pending records awaiting human verification.
- `POST /api/review-queue/{queue_id}/resolve` — Approve or edit low-confidence extractions.
- `POST /api/sync/trigger` — Trigger manual crawl or catalog update.
- `GET /api/sync/status` — Get status of background worker and dropzone watcher.
- `GET /api/stats` — Overall database statistics and OCR success rate.

---

## 12. Installation, Environment Setup & Deployment

### Prerequisites
- **Python**: Version 3.11, 3.12, or 3.13.
- **Node.js**: Version 18.0+ and `npm`.
- **Git**: Installed and configured.
- **Database**: PostgreSQL (Supabase recommended) or built-in local SQLite.

---

### Local Development Setup (PowerShell & Bash)

```bash
# 1. Clone repository
git clone https://github.com/praveen-kumar-007/CALIP-AI-Intelligence.git
cd CALIP-AI-Intelligence

# 2. Setup Python virtual environment
# On Windows:
python -m venv .venv
.venv\Scripts\activate

# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Install & build frontend assets
cd frontend
npm install
npm run build
cd ..

# 5. Configure environment variables
cp .env.example .env
# Edit .env and insert your GROQ_API_KEY, NVIDIA_API_KEY, or GEMINI_API_KEY

# 6. Launch the unified server
# Option A (Windows batch script):
run_app.bat

# Option B (Direct Uvicorn command):
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open **`http://localhost:8000`** in your browser.

---

### Docker Deployment with Docker Compose

CALIP includes a multi-stage `Dockerfile` and `docker-compose.yml`:

```bash
# Launch containerized CALIP production stack
docker compose up -d --build

# View real-time container logs
docker compose logs -f calip
```

---

### Exhaustive Environment Variable Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `"CALIP Legal Intelligence Platform"` | Application title in UI headers and meta tags. |
| `APP_ENV` | `production` | Environment profile (`development`, `staging`, `production`). |
| `HOST` | `127.0.0.1` | Host address to bind the ASGI server. |
| `PORT` | `8000` | Port on which the server listens. |
| `DATABASE_URL` | `sqlite:///./data/calip.db` | Database connection URL. For PostgreSQL with Supabase: `postgresql+psycopg2://user:pass@host:5432/postgres?sslmode=require`. |
| `LLM_PROVIDER` | `groq` | Active LLM provider (`groq`, `nvidia`, `gemini`, `ollama`, `auto`). |
| `GROQ_API_KEY` | `""` | Ultra-fast Groq API key from [console.groq.com](https://console.groq.com/). |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | Model running on Groq LPUs (`qwen/qwen3.8-27b`, `llama-3.3-70b-versatile`). |
| `NVIDIA_API_KEY` | `""` | NVIDIA NIM key from [build.nvidia.com](https://build.nvidia.com/). |
| `NVIDIA_MODEL` | `mistralai/mistral-nemotron` | Model running on NVIDIA NIM infrastructure. |
| `GEMINI_API_KEY` | `""` | Google AI Studio key from [aistudio.google.com](https://aistudio.google.com/). |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model variant. |
| `OLLAMA_BASE_URL`| `http://127.0.0.1:11434` | Endpoint for local private Ollama instances. |
| `OLLAMA_MODEL` | `qwen3:8b` | Ollama model identifier. |
| `AUTO_SYNC_ENABLED`| `true` | Enables background catalog scraper and dropzone watcher. |
| `ENABLE_WINDOWS_OCR`| `true` | Enables native Windows OCR acceleration on Windows hosts. |
| `CHUNK_SIZE` | `600` | Character count per document chunk for embeddings. |
| `CHUNK_OVERLAP` | `100` | Sliding window character overlap across chunks. |

---

## 13. Human-in-the-Loop Review Queue & Provenance Audit

```mermaid
flowchart TD
    Ingest["Raw Ingested Legal Document"] --> Extract["Extraction Pipeline\n(PyMuPDF / OCR / NLP)"]
    Extract --> ConfidenceCheck{"Confidence Score ≥ 0.85?"}
    
    ConfidenceCheck -->|"Yes (High Confidence)"| DirectHydrate["✅ Direct Hydration into Atom\nMarked as DISCOVERED / HYDRATED"]
    ConfidenceCheck -->|"No (Blurry / Ambiguous)"| QueuePush["⚠️ Flagged & Pushed to atom_review_queue\nStatus: PENDING"]
    
    QueuePush --> Studio["🖥️ Human Review Studio\n(/admin/review-queue)"]
    Studio --> ClerkAction{"Clerk Action"}
    
    ClerkAction -->|"Approve Extraction"| Approve["Approve & Hydrate into Atom\nSaved with Auditor ID & Timestamp"]
    ClerkAction -->|"Manual Correction"| Correct["Edit Text / Sections\nSaved as VERIFIED"]
    ClerkAction -->|"Reject False Match"| Discard["Discard Record\nArchived in Audit Trail"]

    style DirectHydrate fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style QueuePush fill:#431407,stroke:#fb923c,stroke-width:2px,color:#fff
    style Approve fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
    style Correct fill:#14532d,stroke:#4ade80,stroke-width:2px,color:#fff
```

In criminal proceedings, erroneous AI hallucination can impact personal liberty. CALIP guarantees that low-confidence, blurry, or ambiguous records are automatically quarantined in `/admin/review-queue`. Court clerks can view the raw scan alongside extracted fields, make edits, and approve with a single click.

---

## 14. SEO, Web Crawlers & AI Manifests (llms.txt)

CALIP is optimized for search engines and modern AI web crawlers:

1. **`llms.txt` & `llms-full.txt`**: Machine-readable markdown manifests enabling LLM agents (Perplexity, Claude, ChatGPT) to crawl and understand the legal repository without parsing heavy HTML.
2. **Dynamic XML Sitemaps**:
   - `/sitemap.xml` (Index)
   - `/sitemap-cases.xml`
   - `/sitemap-documents.xml`
   - `/sitemap-judgments.xml`
   - `/sitemap-orders.xml`
3. **Structured JSON-LD**: Embedded Schema.org `Legislation`, `Court`, and `LegalService` markup on every rendered page.
4. **Permissive Policy in `robots.txt`**: Unrestricted public access for verified research crawlers while disallowing private administrative and review queue endpoints.

---

## 15. Troubleshooting, Performance Tuning & FAQ

### 1. Frontend shows "503 React build not found".
The React application needs to be compiled before FastAPI can serve it:
```bash
cd frontend
npm install
npm run build
cd ..
```

### 2. Can I run CALIP completely offline without internet?
**Yes.** Set `LLM_PROVIDER=ollama` and run an offline model such as `ollama run qwen3:8b`. If no LLM is running, CALIP's built-in **Deterministic Legal Engine** operates locally with sub-5ms latency.

### 3. How do I switch between SQLite and PostgreSQL?
Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/calip_db
```
SQLAlchemy handles connection pooling and schema initialization automatically.

### 4. How does CALIP handle scanned Hindi or Marathi FIRs?
The extraction pipeline detects Devanagari Unicode. Vernacular text is preserved in `original_language_text`, an authoritative English legal translation is generated in `english_translated_text`, and both are indexed for simultaneous search.

---

## 16. License & Governance

This platform is engineered for enterprise legal intelligence, judicial document management, and compliance research. All rights reserved. Built with precision for legal transparency and evidence-backed truth.
