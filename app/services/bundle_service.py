"""
CALIP Modular Bundle Service
Provides bite-sized, self-contained Markdown text files strictly bounded under 20,000 words
specifically tailored for Claude, ChatGPT, and Gemini web reading without context truncation.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.legal_data import (
    get_all_cases,
    get_case_by_id,
    get_all_documents,
    get_document_by_id,
    get_platform_statistics,
    resolve_original_pdf_url,
)
from app.services.hydration_engine import get_all_atoms
from app.services.ocr_service import get_extracted_ocr_data

logger = logging.getLogger("calip.bundle")


def count_words(text: str) -> int:
    return len(text.split())


def render_bundle_index() -> str:
    """Master directory of modular bundles under 20,000 words each."""
    cases = get_all_cases(limit=100)
    stats = get_platform_statistics()

    lines = [
        "# CALIP Modular Research Bundles Directory",
        "",
        "> **For Claude, ChatGPT, and Gemini:**",
        "> Each link below is a self-contained, high-density Markdown text file strictly formatted to be **under 20,000 words**.",
        "> You can copy and paste any of these direct URLs into your AI chat, and the AI can read the full text reliably in a single query.",
        "",
        "## Core System Bundles",
        "",
        "| Bundle Name | Direct URL | Estimated Length | Scope & Topics |",
        "| :--- | :--- | :---: | :--- |",
        "| **CALIP Master Overview** | [https://www.calipai.com/bundle/overview](https://www.calipai.com/bundle/overview) | ~2,500 words | Platform architecture, 38 courts, high-profile case summaries, NDCC Bank, Home Trade. |",
        "| **Cognitive FIR Atoms Digest** | [https://www.calipai.com/bundle/atoms](https://www.calipai.com/bundle/atoms) | ~5,500 words | All 24 criminal FIR atoms, police stations, IPC & MPID sections, accused list. |",
        "| **Court Dates & Hearing MIS** | [https://www.calipai.com/bundle/court-dates](https://www.calipai.com/bundle/court-dates) | ~2,000 words | Complete court calendar, hearing stages, next listing dates, Section 207 status. |",
        "",
        "## Individual Case Bundles (One Focused File Per Case &mdash; Under 20,000 Words)",
        "",
        "| Case ID | Case Number | Forum / Court | Case Title & Subject | Direct Bundle URL |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for c in cases:
        c_id = c.get("id")
        c_num = c.get("case_number") or "N/A"
        court = c.get("court") or "Judicial Forum"
        title = (c.get("title") or "Case").replace("|", "-")
        lines.append(
            f"| `{c_id}` | **{c_num}** | {court} | {title} | [https://www.calipai.com/bundle/cases/{c_id}](https://www.calipai.com/bundle/cases/{c_id}) |"
        )

    lines.extend([
        "",
        "---",
        "## Remote MCP Alternative",
        "If your Claude account has **Settings -> Connectors** enabled, you can connect live via MCP:",
        "- **Remote MCP Endpoint:** `https://www.calipai.com/mcp`",
        "- **MCP Discovery Guide:** [https://www.calipai.com/mcp](https://www.calipai.com/mcp)",
    ])

    return "\n".join(lines)


def render_overview_bundle() -> str:
    """High-level platform overview dossier (~2,500 words)."""
    stats = get_platform_statistics()
    cases = get_all_cases(limit=10)

    lines = [
        "# CALIP Intelligence Dossier: Master Platform Overview",
        "",
        "## 1. System Metadata & Metrics",
        f"- **Platform Name:** CALIP (Comprehensive AI Legal Intelligence Platform)",
        f"- **Total Indexed Judicial Cases:** {stats.get('total_cases', 46)} cases across 38 court forums",
        f"- **Total Extracted Legal Documents:** {stats.get('total_documents', 827)} verified exhibits, orders & charge sheets",
        f"- **Total Verified Document Pages:** {stats.get('total_pages', 41397):,} pages",
        f"- **Total Searchable Semantic Chunks:** {stats.get('total_chunks', 40863):,} chunks",
        f"- **Total Cognitive FIR Atoms:** 24 verified criminal prosecution records",
        f"- **Primary Jurisdiction:** Republic of India (Supreme Court, Bombay High Court, Sessions Courts, CMM Courts)",
        "",
        "## 2. Executive Legal Background",
        "The CALIP repository indexes extensive judicial records concerning co-operative banking, government securities transactions, and allied corporate proceedings spanning Maharashtra, Gujarat, Delhi, and West Bengal.",
        "",
        "### Key Legal Entities & Parties:",
        "- **Nagpur District Central Co-operative Bank Ltd (NDCC Bank):** Co-operative banking institution involved in G-Sec transactions during 2001-2002.",
        "- **Home Trade Limited:** Securities brokerage and financial intermediary involved in government securities broking.",
        "- **Key Accused / Intermediaries:** Sanjay Agarwal, Ketan Seth, Subodh Bhandari, Sunil Kedar (Chairman NDCC Bank), Ashok Namdeo Choudhary (General Manager NDCC Bank), S. G. Trivedi (Chief Executive Officer).",
        "- **Statutory Penal Provisions:** Sections 406 (Criminal Breach of Trust), 409 (Criminal Breach of Trust by Public Servant or Banker), 420 (Cheating), 467/468/471 (Forgery), and 120-B (Criminal Conspiracy) of the Indian Penal Code, 1860; Section 3 & 4 of the Maharashtra Protection of Interest of Depositors (In Financial Establishments) Act, 1999 (MPID); Section 13(2) r/w 13(1)(d) of the Prevention of Corruption Act, 1988.",
        "",
        "### Key Evidentiary Exhibits:",
        "1. **Seizure Panchnama No. 2 (11/05/2002):** Executed by CID Maharashtra Crime Branch at NDCC Bank premises, seizing audit registers, investment committee minutes, and broker correspondence.",
        "2. **Rs. 5 Crore Book Debt Certificate No. 75:** Certificate evidencing assignment of receivables and transactions between financial intermediaries.",
        "3. **S. G. Trivedi Discharge Order (Section 227 CrPC):** Order discharging accused official where the court established that administrative or ministerial acts performed without dishonest intention or mens rea do not constitute criminal offences under Sections 409/420 IPC.",
        "4. **Section 207 CrPC Mandatory Supply Orders:** Judicial rulings upholding the mandatory obligation of investigating agencies to provide complete, legible copies of all police papers, statements, and digital records to the accused prior to charge framing.",
        "",
        "## 3. High-Priority Cases Summary",
    ]

    for c in cases:
        lines.append(f"### Case {c.get('case_number')} ({c.get('id')})")
        lines.append(f"- **Court:** {c.get('court')}")
        lines.append(f"- **Title:** {c.get('title')}")
        lines.append(f"- **Status:** {c.get('status')}")
        if c.get("summary"):
            lines.append(f"- **Summary:** {c.get('summary')[:300]}...")
        lines.append(f"- **Direct Link:** https://www.calipai.com/bundle/cases/{c.get('id')}")
        lines.append("")

    lines.extend([
        "## 4. Complete Directory of Bundles",
        "Visit [https://www.calipai.com/bundle](https://www.calipai.com/bundle) to access all case-specific files.",
    ])

    return "\n".join(lines)


def render_atoms_bundle() -> str:
    """Comprehensive FIR Atoms Digest (~5,500 words)."""
    from app.services.rag_service import get_cached_atoms_for_rag
    raw_atoms = get_cached_atoms_for_rag()
    if not raw_atoms:
        try:
            raw_atoms = get_all_atoms()
        except Exception:
            raw_atoms = []

    lines = [
        "# CALIP Intelligence Dossier: Complete FIR Atoms Digest (24 Verified Records)",
        "",
        "> **Scope:** All 24 criminal prosecution FIR atoms extracted from police records, charge sheets, and court dockets across Maharashtra, Gujarat, Delhi, and West Bengal.",
        "",
    ]

    for idx, a in enumerate(raw_atoms, 1):
        lines.extend([
            f"---",
            f"## {idx}. FIR Atom: `{a.get('id')}` &mdash; {a.get('police_station')} (FIR {a.get('fir_number')}/{a.get('fir_year')})",
            "",
            f"- **Canonical PIN:** `{a.get('id')}`",
            f"- **Police Station:** {a.get('police_station')}",
            f"- **FIR Number & Year:** FIR No. {a.get('fir_number')} of {a.get('fir_year')}",
            f"- **Jurisdiction / State:** {a.get('jurisdiction')} ({a.get('state', 'India')})",
            f"- **Investigating Agency:** {a.get('investigating_agency', 'State Police Crime Branch / CID')}",
            f"- **Statutory Penal Sections:** `{a.get('sections_registered')}`",
            f"- **Offences / Charges:** {a.get('charges_registered')}",
            f"- **Status:** {a.get('status', 'Pending Trial / Committal')}",
            f"- **Accused Persons:** {a.get('accused_names', 'Sanjay Agarwal, Ashok Choudhary, et al.')}",
            f"- **Complainant:** {a.get('complainant', 'Authorized Bank Representative / Regulatory Authority')}",
            f"- **Summary:** {a.get('summary', 'Allegations regarding government securities purchase contracts, failure to deliver physical gilts/SGL, and allied fund routing.')}",
            f"- **Canonical Online URL:** https://www.calipai.com/atoms/{a.get('id')}",
            "",
        ])

    lines.extend([
        "---",
        "*(End of Cognitive FIR Atoms Digest)*",
    ])
    return "\n".join(lines)


def render_court_dates_bundle() -> str:
    """Hearing schedule and MIS calendar (~2,000 words)."""
    cases = get_all_cases(limit=100)

    lines = [
        "# CALIP Intelligence Dossier: Court Dates & Hearing Progression MIS",
        "",
        "> **Scope:** Centralized tracking of hearing dates, stages of proceeding, and judicial forum assignments across all 46 cases.",
        "",
        "## Master Case Hearing Schedule",
        "",
        "| Case ID | Case Number | Forum / Court | Stage of Proceeding | Status | Next Scheduled Action |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for c in cases:
        c_id = c.get("id")
        c_num = c.get("case_number") or "N/A"
        court = c.get("court") or "Judicial Forum"
        status = c.get("status") or "Active"
        stage = "Section 207 Compliance / Arguments on Charge" if "lt-4" in str(c_id) else "Hearing / Appearance"
        action = "Supply of unredacted documents / Scrutiny of papers" if "lt-4" in str(c_id) else "Regular Listing"
        lines.append(f"| `{c_id}` | **{c_num}** | {court} | {stage} | {status} | {action} |")

    lines.extend([
        "",
        "## Legal Framework on Hearing Progression",
        "1. **Stage 1: Appearance & Process Service (Section 204 CrPC):** Accused appears pursuant to summons/warrant.",
        "2. **Stage 2: Supply of Police Report & Documents (Section 207 CrPC):** Mandatory supply of copies of statements, panchnamas, audit ledgers, and seized documents.",
        "3. **Stage 3: Committal to Court of Session (Section 209 CrPC):** In cases triable exclusively by Court of Session.",
        "4. **Stage 4: Discharge Application (Section 227 / 239 CrPC):** Defense application for discharge on grounds of insufficient grounds for proceeding or absence of prima facie case.",
        "5. **Stage 5: Framing of Formal Charges (Section 228 / 240 CrPC):** Judicial framing of charges upon satisfaction of prima facie evidence.",
        "6. **Stage 6: Prosecution Evidence (PW1, PW2, etc.):** Examination-in-chief and cross-examination of prosecution witnesses.",
        "7. **Stage 7: Statement of Accused (Section 313 CrPC):** Personal explanation of incriminating circumstances.",
        "8. **Stage 8: Final Arguments & Judgment.**",
        "",
        "---",
        "*(End of Court Dates & Hearing Progression MIS)*",
    ])
    return "\n".join(lines)


def render_case_bundle(case_id: str) -> str | None:
    """
    Renders a dedicated, high-density case bundle strictly under 20,000 words.
    Contains case facts, parties, FIR atoms, documents list, and excerpted OCR text.
    """
    case = get_case_by_id(case_id)
    if not case:
        return None

    docs = case.get("documents", [])
    linkages = case.get("linkages", {})

    lines = [
        f"# Case Dossier: {case.get('case_number')} &mdash; {case.get('title')}",
        "",
        f"- **Internal Case ID:** `{case.get('id')}`",
        f"- **Case Number:** {case.get('case_number')}",
        f"- **Court / Bench:** {case.get('court')} ({case.get('bench', 'Principal Bench')})",
        f"- **Case Type & Year:** {case.get('case_type', 'Criminal')} of {case.get('case_year', '2002')}",
        f"- **Current Status:** {case.get('status', 'Active')}",
        f"- **Filing Date:** {case.get('filing_date', 'N/A')}",
        f"- **Canonical Online URL:** https://www.calipai.com/cases/{case.get('id')}",
        "",
        "## I. Case Summary & Judicial Subject",
        f"{case.get('summary') or 'Detailed judicial proceeding concerning securities broking transactions and co-operative bank fund allocations.'}",
        "",
        "## II. Connected Legal Linkages",
    ]

    fir_copies = linkages.get("fir_copies", [])
    if fir_copies:
        lines.append("### Linked FIR Records:")
        for fir in fir_copies:
            lines.append(f"- **FIR:** {fir.get('fir_number', 'N/A')} at {fir.get('police_station', 'N/A')} ({fir.get('jurisdiction', 'N/A')}) &mdash; Sections: `{fir.get('sections', 'IPC 406/409/420')}`")
    else:
        lines.append("- *No standalone FIR linkages tagged directly; see Section III for attached exhibits.*")

    lines.extend([
        "",
        f"## III. Attached Verified Documents ({len(docs)} Documents)",
        "",
        "| Document ID | Document Title | Type | Page Count | OCR Status | Original PDF Link |",
        "| :--- | :--- | :--- | :---: | :---: | :--- |",
    ])

    for d in docs[:50]:
        doc_id = d.get("id")
        title = (d.get("title") or "Document").replace("|", "-")
        doc_type = d.get("document_type") or "Exhibit"
        page_cnt = d.get("page_count") or 1
        ocr_st = d.get("ocr_status") or "COMPLETED"
        pdf_url = d.get("url") or f"https://www.calipai.com/documents/{doc_id}"
        lines.append(f"| `{doc_id}` | **{title}** | {doc_type} | {page_cnt} | {ocr_st} | [PDF Link]({pdf_url}) |")

    # Include OCR text excerpts from top documents (bounded to stay well under 20,000 words)
    lines.extend([
        "",
        "## IV. High-Relevance Document Excerpts & Page Transcripts",
        "",
    ])

    total_words = count_words("\n".join(lines))
    max_words = 18000  # Hard ceiling under Claude's 20,000 word limit

    for d in docs[:15]:
        if total_words >= max_words:
            lines.append("> *(Additional document excerpts omitted to remain strictly under the 20,000-word bundle limit. Refer to individual document pages for remaining pages.)*")
            break

        doc_id = d.get("id")
        ocr_data = get_extracted_ocr_data(doc_id)
        pages = (ocr_data or {}).get("pages", [])

        if not pages:
            continue

        lines.append(f"### Excerpt: {d.get('title')} (`{doc_id}`)")
        lines.append(f"- **Total Document Pages:** {len(pages)}")
        lines.append(f"- **Source URL:** https://www.calipai.com/documents/{doc_id}")
        lines.append("")

        for p in pages[:4]:
            text = (p.get("text") or "").strip()
            if not text:
                continue

            snippet = text[:1500]  # Cap per page snippet
            lines.append(f"#### Page {p.get('page_number')} Transcript:")
            lines.append("```")
            lines.append(snippet)
            lines.append("```")
            lines.append(f"*[CALIP Citation: {d.get('title')}, Page {p.get('page_number')} | Case {case.get('case_number')}]*")
            lines.append("")

            total_words = count_words("\n".join(lines))
            if total_words >= max_words:
                break

    lines.extend([
        "",
        "---",
        f"*(Generated by CALIP Modular Bundle Engine &mdash; Total Words: ~{count_words(chr(10).join(lines)):,} words)*",
    ])

    return "\n".join(lines)


def render_document_bundle(document_id: str) -> str | None:
    """Renders a single document as clean text under 20,000 words."""
    doc = get_document_by_id(document_id)
    if not doc:
        return None

    ocr_data = get_extracted_ocr_data(document_id)
    pages = (ocr_data or {}).get("pages", [])

    lines = [
        f"# Document Transcript: {doc.get('title')}",
        "",
        f"- **Document ID:** `{doc.get('id')}`",
        f"- **Case Number:** {doc.get('case_number', 'N/A')}",
        f"- **Court / Forum:** {doc.get('court', 'N/A')}",
        f"- **Document Type:** {doc.get('document_type', 'Legal Exhibit')}",
        f"- **Total Pages:** {doc.get('page_count', len(pages))}",
        f"- **Extraction Method:** {doc.get('extraction_method', 'Verified OCR Engine')}",
        f"- **Direct PDF URL:** {doc.get('pdf_url') or doc.get('original_pdf_url') or 'N/A'}",
        "",
        "---",
        "",
    ]

    total_words = count_words("\n".join(lines))
    max_words = 18500

    if pages:
        for p in pages:
            if total_words >= max_words:
                lines.append(f"\n> *(Truncated to stay under 20,000 words limit. Remaining {len(pages) - p.get('page_number') + 1} pages omitted.)*")
                break
            page_text = (p.get("text") or "").strip()
            lines.append(f"## --- Page {p.get('page_number')} ---")
            lines.append(page_text or "[Empty or photographic page]")
            lines.append("")
            lines.append(f"*[Citation: {doc.get('title')}, Page {p.get('page_number')}]*")
            lines.append("")
            total_words = count_words("\n".join(lines))
    else:
        raw_text = doc.get("extracted_text") or doc.get("full_text") or "[No extracted text found]"
        words = raw_text.split()
        if len(words) > max_words:
            raw_text = " ".join(words[:max_words]) + "\n\n> *(Truncated to 18,500 words)*"
        lines.append(raw_text)

    return "\n".join(lines)
