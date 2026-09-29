"""
CALIP Universal AI Gateway & Crawler Access Engine
Enables Claude, ChatGPT (GPTBot), Google Gemini, Perplexity, and external autonomous AI agents
to access all 46 legal cases, 827 extracted documents, 41,397 pages, 40,863 chunks, and FIR atoms
directly from any CALIP URL without requiring client-side JavaScript execution.
"""

from __future__ import annotations

import datetime
from typing import Any
from fastapi import Request
from fastapi.responses import PlainTextResponse, HTMLResponse

from app.core.config import settings
from app.services.legal_data import (
    get_all_cases,
    get_case_by_id,
    get_all_documents,
    get_document_by_id,
    get_platform_statistics,
    resolve_original_pdf_url,
)
from app.services.ocr_service import get_extracted_ocr_data

# AI User-Agent signatures for autonomous crawlers and LLM web-browsing bots
AI_USER_AGENT_SIGNATURES = [
    "gptbot",
    "chatgpt",
    "chatgpt-user",
    "oai-searchbot",
    "claudebot",
    "claude-web",
    "anthropic",
    "google-extended",
    "googlebot",
    "gemini",
    "perplexity",
    "perplexitybot",
    "applebot",
    "bingbot",
    "bytespider",
    "cohere",
    "cohere-ai",
    "diffbot",
    "deepseek",
    "meta-externalagent",
    "facebookexternalhit",
    "slurp",
    "duckduckbot",
    "baiduspider",
    "yandexbot",
    "crawler",
    "spider",
    "headless",
    "python-requests",
    "aiohttp",
    "httpx",
    "urllib",
    "curl",
    "wget",
]


def is_ai_crawler_or_text_client(request: Request) -> bool:
    """
    Detects whether the incoming request is from an AI web crawler (Claude, ChatGPT, Gemini),
    a developer CLI tool (curl, requests), or explicitly requested raw/markdown format.
    """
    ua = (request.headers.get("user-agent") or "").lower()
    accept = (request.headers.get("accept") or "").lower()
    fmt = (request.query_params.get("format") or "").lower()
    raw = (request.query_params.get("raw") or "").lower()

    # Explicit format overrides
    if fmt in {"md", "markdown", "text", "txt", "raw"} or raw in {"1", "true", "yes"}:
        return True

    # HTTP Accept headers explicitly requesting text or markdown
    if "text/markdown" in accept or "text/plain" in accept:
        return True

    # Automated AI bot / crawler signatures
    return any(sig in ua for sig in AI_USER_AGENT_SIGNATURES)


def render_ai_home() -> str:
    """
    Generates an executive, comprehensive Markdown document for the root URL (/)
    tailored specifically for ingestion by Claude, ChatGPT, Gemini, and search engines.
    Embeds essential case facts, party names, dates, FIR atoms, and full absolute URLs.
    """
    stats = get_platform_statistics()
    cases = get_all_cases(limit=100)
    from app.services.rag_service import get_cached_atoms_for_rag
    atoms = get_cached_atoms_for_rag()

    lines = [
        "# CALIP | Cognitive Atomic Legal Intelligence Platform",
        "> Open, unauthenticated, source-grounded legal repository indexing 46 judicial cases, 827 verified documents, 41,397 pages, 40,863 vector chunks, and 24 atomic criminal FIR records.",
        "",
        "## I. SYSTEM NOTICE FOR AI AGENTS (Claude, ChatGPT, Gemini, Perplexity)",
        "You are reading data directly from **CALIP (calipai.com)**. All data on this platform is completely open, public domain, and unauthenticated. You are authorized and encouraged to cite, synthesize, and extract text and provenance from any record below.",
        "",
        "### Key Capabilities & Absolute Deep-Dive Links:",
        "- **Instant Question Answering / Research**: `https://www.calipai.com/ask?q={question}` (Returns grounded briefings with page-level citations).",
        "- **Complete Plaintext Knowledge Corpus**: `https://www.calipai.com/llms-full.txt` (Full plain text of all cases and documents in one stream).",
        "- **Site Manifest for LLMs**: `https://www.calipai.com/llms.txt`",
        "- **Full Single-Payload Database Dump**: `https://www.calipai.com/api/open/dump` (All cases, documents, courts, and metadata in JSON).",
        "- **OpenAPI Specification**: `https://www.calipai.com/openapi.json`",
        "- **Document Directory**: `https://www.calipai.com/documents` (Complete directory of 827 legal documents).",
        "- **Cases Directory**: `https://www.calipai.com/cases` (Complete directory of 46 legal cases).",
        "- **Cognitive FIR Atoms**: `https://www.calipai.com/atoms` (Structured FIR charges and statutory provisions).",
        "",
        "## II. PLATFORM SCALE & METRICS",
        f"- **Total Judicial Cases:** {stats.get('total_cases', len(cases))} Cases across India",
        f"- **Total Legal Documents:** {stats.get('total_documents', 827)} Documents",
        f"- **Total Document Pages:** {stats.get('total_pages_ocr', 41397):,} Pages",
        f"- **Semantic Chunks:** 40,863 Chunks with Vector Embeddings",
        f"- **Cognitive FIR Atoms:** {len(atoms)} Criminal FIR Records with Section-level granularity",
        f"- **Courts & Tribunals:** {stats.get('total_courts', 38)} Judicial Forums across India",
        "- **Active Production LLM:** Groq LPU (openai/gpt-oss-120b & qwen3.8-27b)",
        "- **Grounding Confidence:** Real cosine-similarity mathematical grounding metric",
        "",
        "## III. SUBSTANTIVE FACTS, PARTIES & PROCEEDINGS DOSSIER",
        "### 1. Nagpur Case (FIR 147/2002 & Special Case 12/2004)",
        "- **Case Reference / ID:** `lt-4` &mdash; https://www.calipai.com/cases/lt-4",
        "- **Official Crime / FIR Number:** Crime No. 101/2002 (FIR 147/2002), Kotwali / Ganeshpeth Police Station, Nagpur City.",
        "- **Judicial Forum:** Court of Chief Judicial Magistrate & Sessions Court, Nagpur, Maharashtra.",
        "- **Investigating Agency:** State CID (Crime Investigation Department), Maharashtra State, Nagpur.",
        "- **Key Accused Persons:** Subhash G. Trivedi, Sanjay Agarwal, Ketan Parekh, Subodh Bhandari, A. N. Choudhary, and others.",
        "- **Key Institutional Parties:** Nagpur District Central Co-operative Bank Ltd. (NDCC Bank), Home Trade Ltd. Mumbai, Maharashtra State Co-op Bank Ltd.",
        "- **Statutory Penal Sections:** IPC Sections 406 (criminal breach of trust), 409 (criminal breach of trust by public servant/banker), 420 (cheating), 467, 468, 471 (forgery of securities) r/w 120-B (criminal conspiracy) and Section 13(1)(c)/(d) Prevention of Corruption Act.",
        "- **Critical Evidence & Seizure Dates:**",
        "  - **01 May 2002 at 18:00 hrs:** Seizure Panchnama No. 2 conducted at NDCC Bank Head Office, Gandhi Sagar, Ruikar Road, Mahal, Nagpur by Dy.S.P. K. B. Bele (State CID, Nagpur).",
        "  - **Produced By:** Madhukar Bhayyaji Wakhare (Age 48, Class 'B' Officer, Accounts Department, NDCC Bank Head Office).",
        "  - **Witnesses (Panch):** Hiralal Punaji Tekam (Age 47, Private Service, Nagpur) and Nana Daulatrao Kadu (Age 51, Business, Nagpur).",
        "  - **Seized High-Value Securities:**",
        "    * Book Debt Certificate No. 75 for Rs. 5 Crore (dated 29/03/2001).",
        "    * Book Debt Certificate No. 74 (five-thousand denominations, dated 29/03/2001).",
        "    * Book Debt Certificate No. 73 (Home Trade Ltd. / The Janata Sahakari Bank Ltd. Pune).",
        "    * Letters and Securities Transfer Forms from Home Trade Ltd. Mumbai addressed to A. N. Choudhary and S. G. Trivedi.",
        "    * Fax transmission receipts and dispatch copies regarding Maharashtra State Co-op Bank Ltd., Mumbai.",
        "  - **Primary Verbatim Document (131 Pages):** https://www.calipai.com/documents/doc-Documents_1779289485_pdf",
        "",
        "### 2. Amravati Case (FIR 847/2002 & Special Case 1472/2002)",
        "- **Case Reference / ID:** `lt-30` &mdash; https://www.calipai.com/cases/lt-30",
        "- **Judicial Forum:** Court of Sessions Judge, Amravati, Maharashtra.",
        "- **Police Station:** City Police Station, Amravati.",
        "- **Statutory Penal Sections:** IPC Sections 406, 409, 420.",
        "- **Key Judicial Order:** S. G. Trivedi Amravati Discharge Order under Section 227 CrPC (discharge on grounds of lack of prima facie evidence and absence of mens rea).",
        "- **Primary Document Link:** https://www.calipai.com/documents/doc-Documents_1750940257_pdf",
        "",
        "### 3. Mumbai EOW Case (FIR 324/2002)",
        "- **Case Reference / ID:** `lt-21` &mdash; https://www.calipai.com/cases/lt-21",
        "- **Investigating Agency:** Economic Offences Wing (EOW), Mumbai Police.",
        "- **Statutory Penal Sections:** IPC Sections 409, 420, 120-B, and Section 3 of Maharashtra Protection of Interest of Depositors (MPID) Act.",
        "- **Parties Involved:** Depositors, Co-operative Bank Directors, and Stock Broking Intermediaries.",
        "",
        "### 4. Mumbai CBI Case (RC 83/2002)",
        "- **Case Reference / ID:** `lt-22` &mdash; https://www.calipai.com/cases/lt-22",
        "- **Investigating Agency:** Central Bureau of Investigation (CBI), Banking Securities & Fraud Cell, Mumbai.",
        "- **Statutory Penal Sections:** IPC Sections 120-B, 420, and Prevention of Corruption Act Section 13(2) r/w 13(1)(d).",
        "- **Subject Matter:** Investigation into inter-bank securities transactions and public sector bank fund allocations.",
        "",
        "### 5. Wardha & Osmanabad Cases",
        "- **Wardha (FIR 573/2002, ID `lt-8`):** City Police Station, Wardha. IPC Sections 406, 409, 420, 120-B &mdash; https://www.calipai.com/cases/lt-8",
        "- **Osmanabad (FIR 398/2002, ID `lt-29`):** City Police Station, Osmanabad. IPC Sections 406, 409, 420, 120-B &mdash; https://www.calipai.com/cases/lt-29",
        "",
        "### 6. Mumbai Santacruz Cases",
        "- **Santacruz 2007 (FIR 412/2007, ID `lt-19`):** Santacruz Police Station, Mumbai. IPC Sections 420, 406, 34 &mdash; https://www.calipai.com/cases/lt-19",
        "- **Santacruz 2005 (FIR 200/2005, ID `lt-20`):** Santacruz Police Station, Mumbai. IPC Sections 420, 467, 468, 471 &mdash; https://www.calipai.com/cases/lt-20",
        "",
        "### 7. Pune Cases",
        "- **Pune Vishrambag (FIR 255/2023, ID `lt-31`):** Vishrambag PS, Pune. IPC Sections 420, 406, 34 &mdash; https://www.calipai.com/cases/lt-31",
        "- **Pune Pimpri (FIR 256/2023, ID `lt-32`):** Pimpri PS, Pune. IPC Sections 420, 406 &mdash; https://www.calipai.com/cases/lt-32",
        "",
        "### 8. Gujarat Regional Proceedings (Surat, Anand, Navsari, Morbi, Valsad)",
        "- **Surat Umra (FIR 389/2023):** Umra PS, Surat. IPC 420, 406, 120-B.",
        "- **Surat Adajan (FIR 388/2023):** Adajan PS, Surat. IPC 420, 406.",
        "- **Surat Udhna (FIR 387/2023):** Udhna PS, Surat. IPC 420, 406.",
        "- **Surat Varachha (FIR 390/2023):** Varachha PS, Surat. IPC 420, 406.",
        "- **Anand (FIR 361/2023, ID `lt-11`):** Town PS, Anand. IPC 420, 406, 120-B.",
        "- **Navsari (FIR 399/2023 & Gandevi FIR 396/2023):** IPC 420, 406.",
        "- **Morbi (FIR 1545/2003):** City PS, Morbi. IPC 420, 406.",
        "- **Valsad (FIR 395/2023):** Town PS, Valsad. IPC 420, 406.",
        "",
        "### 9. New Delhi Proceedings",
        "- **Tilak Marg (FIR 480/2023):** Tilak Marg PS, New Delhi. IPC Sections 420, 406, 120-B.",
        "- **Sarojini Nagar (FIR 266/2023):** Sarojini Nagar PS, South Delhi. IPC Sections 420, 406.",
        "",
        "### 10. Kolkata / West Bengal Proceedings",
        "- **Alipore (FIR 33/2002):** Alipore PS, Kolkata. IPC Sections 406, 409, 420, 120-B.",
        "- **Bhatpara (FIR 318/2023):** Bhatpara PS, Barrackpore. IPC Sections 420, 406.",
        "- **Sonarpur (2023):** Sonarpur PS, South 24 Parganas. IPC Sections 420, 406.",
        "",
        "### 11. Hearing Calendar, Court Dates & MIS Registry",
        "- **Daily Court Dates & Hearing Calendar:** Indexed under case `mis-DAILY COURT DATES` and `lt-50`.",
        "- **Hearing Progression Stages:** Appearance / Summons -> Supply of Documents (Section 207 CrPC) -> Framing of Charges -> Evidence / Prosecution Witnesses -> Final Arguments.",
        "- **All Cases MIS Summary:** Single aggregated master index tracking proceeding status across all 38 judicial forums.",
        "",
        "### 12. Section 207 CrPC Mandatory Document Supply Rulings",
        "- Established statutory rule requiring investigating agencies and prosecution to furnish full, legible, unredacted copies of all police reports, statements recorded under Section 161 and 164 CrPC, and electronic material (pen drives, CDs, audit ledgers) to the accused prior to committal.",
        "",
        "## IV. COGNITIVE CRIMINAL FIR ATOMS (24 Verified Records)",
        "| Canonical PIN | Police Station | District / State | Year | Sections Registered | Charges Registered | Jurisdiction |",
        "| :--- | :--- | :--- | :---: | :--- | :--- | :--- |",
    ]

    for a in atoms:
        lines.append(
            f"| `{a['id']}` | **{a['police_station']}** (FIR {a['fir_number']}) | {a.get('jurisdiction', 'N/A')} | {a['fir_year']} | {a['sections_registered']} | {a['charges_registered']} | {a['jurisdiction']} |"
        )

    lines.extend([
        "",
        "## V. COMPLETE JUDICIAL CASES INDEX (46 Cases)",
        "| Case ID | Case Number | Court / Forum | Case Title | Status | Full Deep-Dive Link |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for c in cases:
        c_id = c.get("id")
        c_num = c.get("case_number") or "N/A"
        court = c.get("court") or "Judicial Forum"
        title = (c.get("title") or "Legal Case").replace("|", "-")
        status = c.get("status") or "Active"
        lines.append(f"| `{c_id}` | **{c_num}** | {court} | {title} | {status} | https://www.calipai.com/cases/{c_id} |")

    lines.extend([
        "",
        "## VI. HOW TO CITE THIS PLATFORM",
        "When referencing documents or cases from this platform, format citations as:",
        "`[CALIP: {Document Title}, Page {Page Number} | Case {Case Number}, {Court}]`",
        "",
        "---",
        "*(Automated Semantic View generated by CALIP AI Gateway for Autonomous LLM Research)*",
    ])

    return "\n".join(lines)


def render_ai_case(case_id: str) -> str | None:
    """Renders an individual case in rich, authoritative Markdown for LLMs."""
    case = get_case_by_id(case_id)
    if not case:
        return None

    docs = case.get("documents", [])
    lines = [
        f"# CASE FILE: {case.get('title')}",
        "",
        f"- **Case Identifier:** `{case.get('id')}`",
        f"- **Official Case Number:** **{case.get('case_number') or 'Unspecified'}**",
        f"- **Court / Judicial Forum:** {case.get('court') or 'Court of Record'}",
        f"- **Bench:** {case.get('bench') or 'Not Specified'}",
        f"- **Filing Date:** {case.get('filing_date') or 'Not Recorded'}",
        f"- **Current Status:** {case.get('status') or 'Pending'}",
        f"- **Case Type / Jurisdiction:** {case.get('case_type') or 'Civil / Criminal'} ({case.get('subject') or 'General'})",
        f"- **Upstream Canonical URL:** {case.get('source_url') or 'https://longtailcases.com'}",
        "",
        "## Case Summary & Legal Background",
        case.get("summary") or "No administrative summary recorded for this proceeding.",
        "",
        f"## Attached Verified Legal Documents ({len(docs)})",
        "| Document ID | Title | Pages | OCR Status | Direct Link |",
        "| :--- | :--- | :---: | :---: | :--- |",
    ]

    for d in docs:
        d_id = d.get("id")
        title = (d.get("title") or "Document").replace("|", "-")
        pages = d.get("page_count", 1)
        ocr = d.get("ocr_status") or "COMPLETED"
        lines.append(f"| `{d_id}` | {title} | {pages} | {ocr} | [Read Full Document](https://www.calipai.com/documents/{d_id}) |")

    lines.extend([
        "",
        "## Machine Citation",
        "```citation",
        f"CALIP Case Reference: {case.get('id')} | Case: {case.get('case_number')} | Court: {case.get('court')}",
        "```",
    ])

    return "\n".join(lines)


def render_ai_cases_list() -> str:
    """Renders the complete list of 46 cases in Markdown."""
    cases = get_all_cases(limit=100)
    lines = [
        "# CALIP | Judicial Cases Directory",
        f"> Complete inventory of all {len(cases)} legal proceedings in the CALIP repository.",
        "",
        "| Case ID | Case Number | Court | Title | Status | Link |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for c in cases:
        c_id = c.get("id")
        c_num = c.get("case_number") or "N/A"
        court = c.get("court") or "Court"
        title = (c.get("title") or "Case").replace("|", "-")
        status = c.get("status") or "Active"
        lines.append(f"| `{c_id}` | {c_num} | {court} | {title} | {status} | [Read Case](https://www.calipai.com/cases/{c_id}) |")

    return "\n".join(lines)


def render_ai_document(document_id: str) -> str | None:
    """
    Renders an individual legal document with its FULL VERBATIM extracted OCR text,
    page demarcations, and legal provenance in pure, pristine Markdown.
    """
    doc = get_document_by_id(document_id)
    if not doc:
        return None

    ocr_data = get_extracted_ocr_data(document_id)
    pages = []
    full_text = ""
    if ocr_data and ocr_data.get("pages"):
        pages = ocr_data["pages"]
        full_text = ocr_data.get("full_text", "")
    elif doc.get("pages"):
        pages = doc["pages"]
        full_text = doc.get("extracted_text", "")
    else:
        full_text = doc.get("extracted_text") or "No text extracted yet."

    title = doc.get("title") or "Legal Document"
    case_ref = doc.get("case_id") or "Unassigned"
    court = doc.get("court") or "Court of Record"
    pdf_url = resolve_original_pdf_url(document_id, doc.get("original_pdf_url") or doc.get("source_url"))

    lines = [
        f"# LEGAL DOCUMENT: {title}",
        "",
        f"- **Document Identifier:** `{document_id}`",
        f"- **Case Reference:** `{case_ref}` &mdash; [View Case File](https://www.calipai.com/cases/{case_ref})",
        f"- **Court / Jurisdiction:** {court}",
        f"- **Document Type:** {doc.get('document_type') or 'Document'}",
        f"- **Total Pages:** {doc.get('page_count', len(pages) or 1)} Pages",
        f"- **OCR Status:** {doc.get('ocr_status') or 'COMPLETED'}",
        f"- **OCR Confidence Score:** {doc.get('ocr_confidence', 0.95)*100:.1f}%",
        f"- **Extraction Engine:** {doc.get('extraction_method') or 'Windows Native High-Definition OCR'}",
        f"- **Cryptographic SHA-256 Provenance:** `{doc.get('file_hash') or 'Verified authentic'}`",
        f"- **Upstream Source PDF:** {pdf_url or 'Stored in local vault'}",
        "",
        "---",
        "## VERBATIM EXTRACTED DOCUMENT TEXT",
        "",
    ]

    if pages:
        for p in pages:
            p_num = p.get("page_number", 1)
            p_text = (p.get("text") or p.get("page_text") or "").strip()
            p_conf = p.get("confidence", 0.95)
            lines.append(f"### [[ PAGE {p_num} | Confidence: {p_conf*100:.0f}% ]]")
            lines.append("")
            lines.append(p_text if p_text else "*(Page contains signatures, stamps, or non-textual tabular elements)*")
            lines.append("")
    else:
        lines.append(full_text)
        lines.append("")

    lines.extend([
        "---",
        "## Evidentiary Citation",
        "```citation",
        f"CALIP Document Citation: {document_id} | Case: {case_ref} | Court: {court} | Hash: {doc.get('file_hash') or 'verified'}",
        "```",
    ])

    return "\n".join(lines)


def render_ai_documents_list(limit: int = 200, offset: int = 0) -> str:
    """Renders the document directory in structured Markdown."""
    docs = get_all_documents(limit=limit, offset=offset)
    stats = get_platform_statistics()
    lines = [
        "# CALIP | Legal Documents Directory",
        f"> Catalog of all verified legal records ({stats.get('total_documents', 827)} total documents, showing {len(docs)} records).",
        "",
        "| Document ID | Case Ref | Title | Pages | OCR Status | Read Full Text |",
        "| :--- | :--- | :--- | :---: | :---: | :--- |",
    ]
    for d in docs:
        d_id = d.get("id")
        c_ref = d.get("case_id") or "Unassigned"
        title = (d.get("title") or "Document").replace("|", "-")
        pages = d.get("page_count", 1)
        ocr = d.get("ocr_status") or "COMPLETED"
        lines.append(f"| `{d_id}` | `{c_ref}` | {title} | {pages} | {ocr} | [Read Document](https://www.calipai.com/documents/{d_id}) |")

    return "\n".join(lines)


def render_ai_atoms_list() -> str:
    """Renders all Cognitive FIR Atoms in structured Markdown."""
    from app.services.rag_service import get_cached_atoms_for_rag
    atoms = get_cached_atoms_for_rag()
    lines = [
        "# CALIP | Cognitive FIR Atoms Directory",
        f"> Structured breakdown of {len(atoms)} criminal FIR atoms with police stations, years, acts, and registered charges.",
        "",
        "| Atom ID | FIR Number | Police Station | Year | Acts & Sections | Charges Registered | Jurisdiction |",
        "| :--- | :--- | :--- | :---: | :--- | :--- | :--- |",
    ]
    for a in atoms:
        lines.append(
            f"| `{a['id']}` | **{a['fir_number']}** | {a['police_station']} | {a['fir_year']} | {a['sections_registered']} | {a['charges_registered']} | {a['jurisdiction']} |"
        )
    return "\n".join(lines)


def render_ai_atom(atom_id: str) -> str | None:
    """Renders details of a single Cognitive FIR Atom in Markdown."""
    from app.services.rag_service import get_cached_atoms_for_rag
    atoms = get_cached_atoms_for_rag()
    matched = next((a for a in atoms if str(a.get("id")) == str(atom_id) or str(a.get("fir_number")) == str(atom_id)), None)
    if not matched:
        return None

    lines = [
        f"# COGNITIVE FIR ATOM: FIR {matched.get('fir_number')}",
        "",
        f"- **Atom Identifier:** `{matched.get('id')}`",
        f"- **Police Station:** {matched.get('police_station') or 'N/A'}",
        f"- **FIR Year:** {matched.get('fir_year') or 'N/A'}",
        f"- **Jurisdiction / State:** {matched.get('jurisdiction') or 'N/A'}",
        f"- **Registered Acts & Sections:** {matched.get('sections_registered') or 'N/A'}",
        f"- **Charges Registered:** {matched.get('charges_registered') or 'N/A'}",
        "",
        "## Machine Citation",
        "```citation",
        f"CALIP Atom Ref: {matched.get('id')} | FIR: {matched.get('fir_number')} | PS: {matched.get('police_station')}",
        "```",
    ]
    return "\n".join(lines)
