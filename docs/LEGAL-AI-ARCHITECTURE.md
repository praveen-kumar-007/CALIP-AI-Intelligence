# Legal AI Architecture Design

## 1. Product objective

Build a public legal intelligence platform that ingests case and document content, extracts legal metadata, supports grounded retrieval, and answers questions with evidence-backed citations instead of model memory alone.

## 2. Core principles

- preserve source provenance for every extracted fact
- favor server-rendered HTML for legally important content
- separate public site surfaces from internal admin or private systems
- treat the relational database as the source of truth and the vector layer as retrieval acceleration
- provide citations for every answer where evidence exists
- never invent legal outcomes when the corpus is insufficient

## 3. High-level architecture

Public Website
→ Search Index / Sitemap / Readable HTML
→ FastAPI application layer
→ PostgreSQL relational database
→ Vector database (pgvector or Qdrant)
→ Ingestion and OCR workers
→ Knowledge graph and relationship layer
→ RAG and answer-generation layer
→ Local or external LLM provider abstraction

## 4. Site and public content architecture

The public website exposes stable canonical URLs and AI-readable metadata across the legal data model. Every page should include:

- title and description metadata
- H1 heading and structured headings
- breadcrumb navigation
- case or document metadata
- source URL and publication date
- clear page/document references
- JSON-LD structured data

## 5. Ingestion engine design

Each document should pass through the following pipeline:

URL/PDF/File
→ Downloader
→ Validation
→ SHA-256 hashing and duplicate detection
→ PDF type detection
→ text extraction
→ OCR fallback if required
→ cleaning and normalization
→ segmentation and legal metadata extraction
→ entity extraction
→ relationship extraction
→ chunking
→ embedding generation
→ vector indexing
→ knowledge graph update
→ search indexing
→ public HTML/API publication

## 6. Supported content types

- PDF (text-based)
- scanned PDF
- image-heavy PDF
- HTML
- DOC/DOCX when available
- plain text
- future document formats

## 7. Legal metadata model

At minimum, store:

- case number and year
- court and bench
- filing and judgment dates
- parties, judges, and advocates
- issues, acts, and provisions
- document type and document relationships
- source URL and canonical URL
- provenance and processing metadata

## 8. Entity extraction strategy

Entity extraction should identify and score:

- courts
- judges
- benches
- advocates
- parties
- acts and sections
- rules and regulations
- legal issues and decisions
- cited authorities and precedents
- organizations and locations

The system should retain both the extracted entity and confidence, source document, page number, and extraction method.

## 9. Taxonomy and ontology

The taxonomy should be hierarchical and extensible. The ontology should model legal relationships as typed edges with stable identifiers and provenance. This allows retrieval by both keyword and semantic similarity while preserving citation structure.

## 10. Semantic layer

Legal text should be chunked into meaningful sections instead of embedding entire documents as a single vector. The embedding layer should include page, court, case, document type, and legal topic data to support metadata-aware retrieval.

## 11. Vector search and metadata filters

Vector search supports:

- semantic search
- keyword search
- hybrid search
- case metadata filters
- court and date filters
- legal provision filters

## 12. RAG system design

The RAG system should retrieve from multiple sources, then rank them by relevance and answerability. It should then generate a response that includes the case, document, page, date, court, and source URL when available.

## 13. AI safety rules

- source document always distinguished from extracted fact and model-generated summary
- legal answers must be grounded in the corpus
- when evidence is missing, return a clear insufficiency statement
- no court-outcome prediction or automatic legal advice
- if conflicting documents exist, surface the conflict explicitly

## 14. Public API and feed strategy

Public read-only endpoints and machine-readable feeds power search engine discovery, AI crawlers, and external integrations. The API should support filtering, sorting, pagination, stable IDs, document URLs, page references, and updated timestamps.

## 15. robots.txt and sitemap design

The public site should expose a discoverable crawl surface while blocking private routes and admin systems. The sitemap should be decomposed into case, document, judgment, and order feeds to improve discovery and AI accessibility.

## 16. HTML and JSON-LD strategy

Every legal page should be server-rendered, canonicalized, and embedded with structured metadata. Where legal facts are presented, they should be accompanied by source references and document provenance.

## 17. Security and governance

- block admin, internal, and sensitive directories
- sanitize uploads and scan them
- prevent arbitrary code execution through validation and separation of storage locations
- keep public assets independent from internal configurations and private files

## 18. Local AI provider abstraction

The system should support a provider abstraction that can route to:

- local Ollama
- local PyTorch / GPU-backed models
- external API-based providers

No hard dependency should be introduced on a single vendor or model provider.

## 19. Implementation roadmap

1. Scaffold the app and baseline routes
2. Define canonical data model and legal taxonomy
3. Build ingestion pipeline and duplicate detection
4. Add OCR and metadata extraction
5. Enable vector search and hybrid retrieval
6. Add knowledge graph and relationships
7. Build public pages and JSON-LD output
8. Provide public APIs and sitemap feeds
9. Add RAG answer layer with citations
10. Validate with curated legal datasets and security checks

## 20. Deployment strategy

Deploy the web app and public site with a separation between public content and internal ingestion infrastructure. Use PostgreSQL as the authoritative datastore, pgvector for embeddings, and optional Neo4j only when graph complexity justifies it.
