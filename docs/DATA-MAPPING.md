# CALIP & LongtailCases Data Mapping & Architecture Specification

## 1. Existing Architecture Audit

### Workspace Analysis
- **Framework**: FastAPI (v0.141.1) with Uvicorn, Jinja2 templates, and static assets.
- **Hardware & Environment**:
  - Windows 11 with Python 3.13.13.
  - NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA enabled with PyTorch 2.14.0+cu132).
  - Local Ollama runtime running on port 11434 with `qwen3:8b` active and verified.
  - PyMuPDF (1.28.2), Sentence-Transformers (6.1.0), OpenCV, BeautifulSoup4, Requests, SQLAlchemy, SQLite/pgvector ready.
- **Upstream Target (`longtailcases.com`)**:
  - Live inspection confirms 42 primary section and case nodes across 10 top-level legal groups.
  - Deep nested hierarchy: Category -> Case -> Folder (`/get-folder-documents/{id}`) -> Sub-folder (`/get-sub-folder-documents/{id}`) -> Child Sub-folders -> Documents / PDFs (`/uploads/...`).
  - Contains text PDFs, scanned PDFs, MIS control summaries, daily court date sheets, and case documents (FIR, charge sheets, roznama, trial exhibits, bail petitions, orders, judgments).

---

## 2. Page Map (Server-Rendered HTML & AI-Readable)

- `/` : Unified intelligence portal featuring live case counts, quick search, recent filings, and longtail hierarchy navigation.
- `/cases` : Searchable index of all legal cases with filters (Court, State, Year, Status).
- `/cases/{case_id}` : Full case record with court, parties, bench, timeline, citations, acts/sections, and attached documents.
- `/judgments` : Repository of authoritative judgments with filterable issues and precedents.
- `/judgments/{judgment_id}` : Server-rendered judgment page with issues, arguments, reasoning, decision, and PDF viewer.
- `/orders` : Chronological listing of interim and final court orders.
- `/orders/{order_id}` : Order details with bench, directions, and source document links.
- `/applications` : Petitions, bail pleas, transfer petitions, and miscellaneous applications.
- `/applications/{application_id}` : Application detail with filing date, prayer, and status.
- `/courts` : Hierarchy of courts (Supreme Court, High Courts, District/Sessions/Magistrate Courts).
- `/courts/{court_id}` : Court profile with case rosters and judge assignments.
- `/acts` : Statutory repository (IPC, CrPC, NI Act, Specific Relief Act, etc.).
- `/sections` : Specific statutory sections cited in proceedings.
- `/documents` : Complete archive of all ingested legal documents and PDFs.
- `/documents/{document_id}` : Machine-readable document page with full OCR/text, provenance hash, metadata, and page navigation.
- `/longtail` : Exact mirror of `longtailcases.com` hierarchical folder tree with interactive drill-down.
- `/search` : Hybrid search page (full-text keyword + semantic vector + graph relationship filter).
- `/ai-research` : Interactive RAG interface with source-grounded answers, exact page citations, and evidence verification.
- `/admin/dashboard` : Pipeline status, OCR monitoring, crawler control, and duplicate management.
- `/about` : System provenance, legal disclaimer, and safety rules.
- `/robots.txt` : AI-crawler friendly policy permitting public content while protecting internal endpoints.
- `/sitemap.xml` & child sitemaps : XML index for discovery by search engines and AI crawlers.

---

## 3. Document Map & Longtail Hierarchy

### Top-Level Sections from `longtailcases.com`
1. **MIS & Control Sheets**:
   - `Summary All Cases` (`/uploads/new_mis/MIS.pdf`)
   - `Index of Documents uploaded on website` (`/uploads/new_mis/DAILY COURT DATES.pdf`)
2. **Court Dates List (Yearly, Casewise, Weekly)**:
   - `/documents/50` (Period wise court dates)
   - `/documents/51` (Court dates CASEWISE)
   - `/documents/52` (WEEKLY COURT DATES)
3. **Library of Judgements**:
   - `/documents/49` (Supreme Court & High Court judgments)
4. **Library of HTL Documents**:
   - `/documents/48` (Home Trade Company Documents)
   - `/documents/61` (Home Trade MOA and AOA)
5. **Supreme Court (Group Applications)**:
   - `/documents/36` (Transfer Petition)
   - `/documents/37` (Modification Application)
   - `/documents/38` (Writ Petition)
   - `/documents/42` (Misc Applications and Orders)
6. **High Court**:
   - `/documents/45` (Group Applications and Orders)
7. **Maharashtra State Cases**:
   - `/documents/4` (Nagpur - 147/2002)
   - `/documents/8` (Wardha - 573/2002)
   - `/documents/19` (Santacruz - 412/2007)
   - `/documents/20` (Santacruz - 200/2005)
   - `/documents/21` (EOW - 324/2002)
   - `/documents/22` (CBI Mumbai - 83/2002)
   - `/documents/29` (Osmanabad - 398/2002)
   - `/documents/30` (Amravati - 847/2002)
   - `/documents/31` (Pune Vishrambag - 255/23)
   - `/documents/32` (Pune Pimpri - 256/2023)
   - `/documents/34` (Group Orders)
8. **Gujarat State Cases**:
   - Anand (`/documents/11`), Udna (`/documents/12`), Adajan (`/documents/13`), Umra (`/documents/14`), Varacha (`/documents/15`), Valsad (`/documents/16`), Gandevi (`/documents/17`), Navsari (`/documents/18`), Morbi (`/documents/33`)
9. **Delhi Cases**:
   - Patiala House (`/documents/26`), Sarojini Nagar (`/documents/27`)
10. **Kolkata Cases**:
    - Bhat Para (`/documents/23`), Sonar Pur (`/documents/24`), Alipore (`/documents/25`)
11. **Cheque Bounce & Civil Suit Cases**:
    - Umra (`/documents/54`), Valsad (`/documents/55`), Varachha (`/documents/56`), Wardha (`/documents/57`, `/documents/58`), Gandevi (`/documents/59`)

### Recursive Tree Structure
```
Category (e.g., Maharashtra)
  └── Case Node (e.g., Nagpur 147/2002)
        └── Folder (e.g., Applications & Orders - Sanjay Agarwal)
              └── Sub-folder L1 (e.g., Sessions Court)
                    └── Sub-folder L2 (e.g., 1. SPLIT OF CHARGE SHEET)
                          ├── Application PDF
                          └── Order PDF
```

---

## 4. Relational Database Schema

Authority datastore implemented with SQLAlchemy (SQLite out-of-the-box, seamlessly targeting PostgreSQL + pgvector):

1. `cases`: `case_id`, `case_number`, `case_type`, `case_year`, `court_id`, `title`, `bench`, `filing_date`, `status`, `summary`, `source_url`, `created_at`, `updated_at`.
2. `courts`: `court_id`, `name`, `jurisdiction`, `court_type` (Supreme, High, District, Magistrate, Tribunal), `state`, `city`.
3. `parties`: `party_id`, `case_id`, `name`, `role` (Petitioner, Respondent, Intervener, Accused), `type` (Individual, Corporate, State).
4. `judges`: `judge_id`, `name`, `court_id`, `designation`.
5. `advocates`: `advocate_id`, `name`, `bar_council_id`, `role`.
6. `documents`: `document_id`, `case_id`, `document_type`, `title`, `document_number`, `document_date`, `source_url`, `pdf_url`, `local_pdf_path`, `file_hash` (SHA-256), `page_count`, `ocr_required`, `ocr_status`, `ocr_confidence`, `extraction_method`, `created_at`, `updated_at`.
7. `document_pages`: `page_id`, `document_id`, `page_number`, `page_text`, `has_images`, `ocr_confidence`.
8. `document_chunks`: `chunk_id`, `document_id`, `page_number`, `chunk_index`, `chunk_text`, `token_count`, `section_title`, `embedding_id`.
9. `judgments`: `judgment_id`, `case_id`, `document_id`, `title`, `judgment_date`, `bench`, `summary`, `issues`, `findings`, `reasoning`, `decision`, `directions`.
10. `orders`: `order_id`, `case_id`, `document_id`, `order_date`, `bench`, `order_type`, `summary`, `directions`.
11. `applications`: `application_id`, `case_id`, `document_id`, `title`, `applicant`, `prayer`, `filing_date`, `status`.
12. `acts`: `act_id`, `title`, `year`, `short_code`, `category`.
13. `sections`: `section_id`, `act_id`, `section_number`, `title`, `description`.
14. `entities`: `entity_id`, `entity_type`, `name`, `normalized_name`, `confidence`, `source_document_id`, `page_number`.
15. `relationships` (Knowledge Graph Edges): `edge_id`, `subject_id`, `subject_type`, `predicate`, `object_id`, `object_type`, `confidence`, `source_document_id`, `page_number`.
16. `longtail_folders`: `folder_id`, `parent_id`, `case_id`, `title`, `url`, `folder_type` (root, folder, subfolder), `level`, `pdf_count`.
17. `processing_jobs`: `job_id`, `document_id`, `stage`, `status`, `error_message`, `started_at`, `completed_at`.

---

## 5. Legal Taxonomy

- **LEGAL**
  - **COURTS**
    - Supreme Court of India
    - High Courts (Bombay High Court, Gujarat High Court, Delhi High Court, Calcutta High Court)
    - Sessions & District Courts (Nagpur, Wardha, Pune, Anand, Surat, Patiala House, Alipore)
    - Magistrate Courts (Judicial Magistrate First Class, Metropolitan Magistrate)
    - Special Courts (CBI Courts, EOW Courts, MPID Special Courts)
  - **DOCUMENT TYPES**
    - Judgment (Final Judgment, Reported Precedent)
    - Order (Interim Order, Status Quo, Bail Order, Charge Framing Order)
    - Application (Bail Application, Transfer Petition, Modification, Discharge)
    - Police / Investigation Record (FIR, Charge Sheet, Seizure Panchnama, Mother File Exhibits)
    - Roznama (Daily Court Proceedings, Physical Court Minutes)
    - Corporate & Statutory Document (MOA, AOA, Auditor Notes)
  - **AREAS OF LAW**
    - Criminal Law (IPC, CrPC, Prevention of Corruption, MPID Act)
    - Commercial & Negotiable Instruments (Section 138 NI Act)
    - Constitutional Law (Articles 32, 226, 14, 21)
    - Civil & Corporate Law (Specific Relief Act, Companies Act)
  - **LEGAL PROVISIONS**
    - Acts, Sections, Rules, Schedules

---

## 6. Legal Ontology & Knowledge Graph Design

Graph relationships modeled with typed RDF-style triples with explicit provenance:
- `CASE` — `filed_in` → `COURT`
- `CASE` — `has_judge` → `JUDGE`
- `CASE` — `has_party` → `PARTY`
- `CASE` — `has_document` → `DOCUMENT`
- `CASE` — `has_judgment` → `JUDGMENT`
- `CASE` — `has_order` → `ORDER`
- `CASE` — `has_folder` → `FOLDER`
- `FOLDER` — `has_subfolder` → `SUBFOLDER`
- `FOLDER / SUBFOLDER` — `contains_pdf` → `DOCUMENT`
- `JUDGMENT` — `cites` → `PRECEDENT_CASE`
- `JUDGMENT` — `interprets` → `SECTION`
- `DOCUMENT` — `references` → `ACT / PROVISION`
- `DOCUMENT_CHUNK` — `derived_from` → `DOCUMENT_PAGE`

---

## 7. Pluggable OCR Pipeline & "My OCR" Integration

### Architecture:
```
PDF Document
    │
    ├── 1. Digital Text Check (PyMuPDF `page.get_text()`)
    │     ├── If selectable text found (> 80 characters/page)
    │     └── Store extraction_method="pymupdf_text"
    │
    └── 2. Scanned / Image Fallback
          ├── A. "My OCR" Pluggable Hook:
          │      - Environment variable `USER_OCR_COMMAND` (e.g., custom executable / Python script)
          │      - API / Python hook `register_custom_ocr(handler_func)`
          │      - User provides image/PDF -> receives page-mapped text & confidence
          │
          ├── B. Local Ollama Vision Fallback (e.g. Qwen2-VL / Llama-Vision when present)
          │
          └── C. PyMuPDF Native Pixmap + Tesseract/OpenCV adapter
                 - Automatic grayscale, adaptive thresholding, deskewing
                 - Page-by-page mapping with confidence score
```
- **Provenance Guaranteed**: Output stores `ocr_required`, `ocr_status`, `ocr_confidence`, `extraction_method`, and raw page numbers.

---

## 8. Embedding & Vector Database Design

- **Chunking Strategy**: Semantic boundary chunking (500–800 tokens with 100-token overlap, respecting paragraph & legal section boundaries).
- **Embedding Model**: Local `sentence-transformers` (`all-MiniLM-L6-v2` or `paraphrase-multilingual-MiniLM-L12-v2`) with GPU acceleration on RTX 3050 CUDA.
- **Storage Layer**:
  - SQLite with vector cosine similarity matrix (zero external dependency for fast local dev).
  - Native pgvector table adapter when connected to PostgreSQL.
  - Every vector entry links `chunk_id`, `document_id`, `case_id`, `court`, `date`, `page_number`, `source_url`.

---

## 9. RAG Architecture (Source-Grounded Legal Answers)

```
User Query
    │
    ├── 1. Query Analyzer & Intent Classifier
    │     (Identifies Case No, Court, Section, Legal Issue)
    │
    ├── 2. Hybrid Retrieval:
    │     ├── Full-Text Keyword Match (BM25 / SQLite FTS)
    │     ├── Semantic Vector Search (Cosine Similarity top-k)
    │     └── Knowledge Graph Traversal (Entities, Citations, Precedents)
    │
    ├── 3. Reranking & Evidence Filter (Threshold score)
    │
    ├── 4. Grounded Context Assembly (Document title, Court, Date, Page, Chunk text)
    │
    ├── 5. Local LLM Generation via Ollama (`qwen3:8b` on RTX 3050)
    │     - Strict prompt: Answer strictly from provided snippets.
    │     - If evidence is absent: State explicitly that available documents do not establish the answer.
    │
    └── 6. Output Verification & Citation Attribution
          - Cites: Case, Document Title, Page Number, Date, Court, PDF Source URL.
```

---

## 10. Public API Design

- `GET /api/cases` : List cases with filtering (`court`, `case_type`, `year`, `status`), pagination (`limit`, `offset`).
- `GET /api/cases/{case_id}` : Full case record with document tree, citations, and metadata.
- `GET /api/documents` : List documents with search and type filters.
- `GET /api/documents/{document_id}` : Detailed document record with extracted text, chunks, and provenance hash.
- `GET /api/judgments` & `/api/judgments/{judgment_id}` : Judgment details with issues and decisions.
- `GET /api/orders` & `/api/orders/{order_id}` : Order records and directions.
- `GET /api/search` : Multi-modal search endpoint (`q`, `type`, `court`, `semantic=true`).
- `GET /api/rag/ask` & `POST /api/rag/ask` : Question-answering endpoint with source-grounded citations.
- `GET /api/longtail/catalog` : Recursive longtailcases catalog tree (categories, cases, folders, PDFs).
- `POST /api/longtail/harvest` : Ingestion worker trigger to crawl and index longtail cases.
- `POST /api/ocr/custom` : Ingest OCR results directly from user custom OCR pipeline.

---

## 11. SEO, AI Crawlers, Robots.txt & Sitemaps

- Standardized `robots.txt` allowing AI crawlers and search engines on `/`, `/cases`, `/documents`, `/judgments`, `/orders`, `/longtail`, `/api`.
- Disallowing `/admin/`, `/private/`, `/.env`, `/internal/`.
- Decomposed sitemaps:
  - `/sitemap.xml` (Index)
  - `/sitemap-cases.xml`
  - `/sitemap-documents.xml`
  - `/sitemap-judgments.xml`
  - `/sitemap-orders.xml`
- Canonical `<link rel="canonical" href="...">` on every page.
- Schema.org JSON-LD structured data (`CreativeWork`, `Legislation`, `DigitalDocument`, `BreadcrumbList`).

---

## 12. Security & Provenance Design

- SHA-256 cryptographic hashing on every ingested PDF to prevent duplication.
- File upload sanitization: strict mime-type validation, size limits (max 50MB), filename normalization, path traversal prevention.
- Environment separation: credentials and API keys stored in `.env` (never exposed via API or UI).
- Read-only public APIs: state-modifying actions isolated to authenticated/admin endpoints.
- Read-only document storage preserving the unmodified original binary file alongside extracted text.
