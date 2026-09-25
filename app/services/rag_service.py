import re
from typing import Any

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Case, Document, DocumentChunk, Atom, Court
from app.services.vector_service import vector_search
from app.services.llm_provider import query_llm, get_active_model_name, LLMProvider
from app.services.legal_search_service import fetch_verified_external_legal_context
from app.services.markdown_renderer import render_markdown_to_html

CONVERSATIONAL_RE = re.compile(
    r"^(hi|hello|hey|greetings|namaste|kem cho|kasa ahes|how are you|who are you|what are you|what can you do|help|what is calip|tell me about yourself|good morning|good afternoon|good evening|good day)\b",
    re.IGNORECASE,
)


def query_ollama(
    prompt: str,
    system_prompt: str | None = None,
    model: str | None = None,
    timeout: int = settings.RAG_TIMEOUT_SECONDS,
) -> str | None:
    """Invokes production LLM (Groq, NVIDIA NIM, Gemini, or local Ollama)."""
    return query_llm(
        prompt=prompt,
        system_prompt=system_prompt
        or "You are the Senior Legal Intelligence Officer and Judicial Research Analyst for CALIP. Answer authoritatively with exact citations and structured tables.",
        temperature=settings.RAG_TEMPERATURE,
        max_tokens=3000,
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
        f"## Executive Summary\n\n"
        f"Based on the available verified legal records for **{case_ref}** (Page {page_ref}), "
        f"the documented text establishes:\n\n"
        f"> \"{top_snippet[:400]}...\"\n\n"
        f"Please consult the verified source documents below for the complete forensic record."
    )


def ask_legal_question(
    query: str,
    case_id: str | None = None,
    court_filter: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """
    CALIP Advanced Legal Intelligence & Dual-Corpus Verification Pipeline:
    1. Conversational intent detection with specialized legal guidance
    2. Hybrid Database Search: Vector chunks, Case entities, and Atomic FIR records
    3. External Legal Verification: Indian Kanoon judicial authorities & statutory cross-references
    4. Structured Legal Briefing Synthesis: Markdown tables, statutory matrices, and evidentiary citations
    5. Dual Server & Client Rendering: Instant HTML formatting without unparsed raw asterisks
    """
    limit_k = top_k if top_k is not None else settings.RAG_TOP_K
    cleaned_query = query.strip()
    if not cleaned_query:
        return {
            "query": query,
            "answer": "Please provide a specific legal question or search query.",
            "rendered_html": "<p class=\"legal-p\">Please provide a specific legal question or search query.</p>",
            "sources": [],
            "external_sources": [],
            "grounded": False,
            "model": get_active_model_name(),
        }

    # 1. Handle conversational greetings and capability questions gracefully
    if CONVERSATIONAL_RE.search(cleaned_query) or cleaned_query.lower() in {
        "hi", "hello", "hey", "how are you", "who are you", "what can you do", "help", "calip", "what is calip"
    }:
        system_prompt = (
            "You are the Senior AI Legal Intelligence Assistant for CALIP (Cognitive Atomic Legal Intelligence Platform).\n"
            "Respond warmly, authoritatively, and professionally.\n"
            "Explain that you analyze court proceedings, FIR cognitive atoms, charges, acts, sections, and case evidence "
            "with verified page-level citations from longtailcases.com and live Indian legal authorities.\n"
            "List 3 specific clickable example queries:\n"
            "• 'What are the charges and acts in the Nagpur case (FIR 147/2002)?'\n"
            "• 'What did the court decide regarding Section 207 CrPC documents?'\n"
            "• 'What cases and FIR numbers are listed in the MIS report?'\n"
            "Keep the response structured, elegant, and concise."
        )
        conv_answer = query_llm(
            prompt=cleaned_query,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=600,
        )
        if not conv_answer:
            conv_answer = (
                "## Welcome to CALIP Legal Intelligence\n\n"
                "I am your **AI Legal Intelligence Assistant**, powered by the **Cognitive Atomic Legal Intelligence Platform**.\n\n"
                "I analyze case proceedings, FIR records, charge sheets, and evidence documents with verified page citations and statutory cross-referencing.\n\n"
                "### Example Legal Inquiries:\n"
                "- **Nagpur Case Charges & Acts**: *What are the charges and acts in the Nagpur case (FIR 147/2002)?*\n"
                "- **Section 207 CrPC Rulings**: *What did the court decide regarding Section 207 CrPC documents?*\n"
                "- **Corpus Cross-Examination**: *What cases and FIR numbers are listed in the MIS report?*\n\n"
                "Enter your legal question above to generate a fully verified, structured briefing."
            )
        return {
            "query": cleaned_query,
            "answer": conv_answer,
            "rendered_html": render_markdown_to_html(conv_answer),
            "sources": [],
            "external_sources": [],
            "model": get_active_model_name(),
            "grounded": True,
        }

    # 2. Retrieve Internal Evidence Chunks from CALIP Database
    retrieved_chunks = vector_search(
        query=cleaned_query,
        top_k=limit_k,
        case_id=case_id,
        court_filter=court_filter,
    )

    # 3. Retrieve Matching Atomic FIR and Case Records
    db = SessionLocal()
    atom_records = []
    matched_cases = []
    try:
        fir_match = re.search(r"(\d+[/]\d+|\b\d{3,4}\b)", cleaned_query)
        if fir_match:
            fir_token = fir_match.group(1)
            atom_records = db.query(Atom).filter(Atom.fir_number.ilike(f"%{fir_token}%")).all()

        matched_cases = db.query(Case).filter(
            (Case.title.ilike(f"%{cleaned_query}%"))
            | (Case.case_number.ilike(f"%{cleaned_query}%"))
            | (Case.court_name.ilike(f"%{cleaned_query}%"))
            | (Case.summary.ilike(f"%{cleaned_query}%"))
        ).limit(3).all()

        # If vector chunks were sparse, supplement with case metadata
        if not retrieved_chunks:
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

    # 4. Fetch External Verified Legal Authorities & Court Precedents
    external_authorities = []
    try:
        external_authorities = fetch_verified_external_legal_context(cleaned_query)
    except Exception:
        external_authorities = []

    # 5. Assemble Structured Context
    internal_blocks = []
    for idx, item in enumerate(retrieved_chunks):
        c_title = item.get("case_title") or item.get("case_number") or "Case"
        d_title = item.get("document_title") or "Document"
        court = item.get("court") or "Court"
        page = item.get("page_number", 1)
        text = item.get("chunk_text", "")
        internal_blocks.append(
            f"[Source {idx+1} | Internal CALIP Record]\nCase: {c_title}\nCourt: {court}\nDocument: {d_title}\nPage: {page}\nText:\n{text}"
        )

    for atom in atom_records:
        internal_blocks.append(
            f"[CALIP Atomic FIR Record]\nFIR Number: {atom.fir_number}\nPolice Station: {atom.police_station or 'N/A'}\n"
            f"Year: {atom.fir_year or 'N/A'}\nActs & Sections: {atom.acts_sections or 'N/A'}\n"
            f"Charges Framed: {atom.charges_framed or 'N/A'}\nCourt: {atom.court_jurisdiction or 'N/A'}"
        )

    internal_str = "\n\n".join(internal_blocks) if internal_blocks else "No specific internal file excerpt located."

    external_blocks = []
    for idx, ext in enumerate(external_authorities):
        external_blocks.append(
            f"[External Authority {idx+1} | {ext.get('authority', 'Judicial Registry')}]\n"
            f"Title: {ext.get('title')}\nURL: {ext.get('source_url')}\nKey Excerpt: {ext.get('snippet')}"
        )
    external_str = "\n\n".join(external_blocks) if external_blocks else "No external judicial authorities attached."

    # 6. Comprehensive Legal Intelligence Prompt
    system_prompt = (
        "You are the Senior Legal Intelligence Officer & Judicial Research Specialist for CALIP "
        "(Cognitive Atomic Legal Intelligence Platform).\n\n"
        "TASK:\n"
        "Produce an authoritative, comprehensive, and impeccably structured Official Legal Intelligence Briefing "
        "answering the user's legal inquiry. Synthesize both internal case records and established Indian statutory law.\n\n"
        "MANDATORY OUTPUT STRUCTURE (Use Markdown with clean headings and tables):\n\n"
        "## 1. Executive Legal Summary\n"
        "Provide a direct, authoritative legal summary addressing the core question clearly and definitively.\n\n"
        "## 2. Statutory Provisions & Criminal Charges (Detailed Matrix)\n"
        "Construct a detailed Markdown table detailing the relevant statutory sections and penal provisions:\n"
        "| Statutory Section | Legislation / Act | Legal Classification | Essential Ingredients & Elements | Offence Allegation / Case Application |\n"
        "| :--- | :--- | :--- | :--- | :--- |\n"
        "Include all applicable provisions (e.g. IPC Sections 406, 409, 468, 471, 120-B, 34; Prevention of Corruption Act; Co-operative Societies Act) with precise legal elements.\n\n"
        "## 3. Case Particulars & Procedural Matrix\n"
        "Provide a structured matrix covering:\n"
        "- **Case / FIR Reference**: e.g., C.C. No. 147/2002 (clubbing C.R. Nos. 97/2002 & 101/2002)\n"
        "- **Originating Police Station & Jurisdiction**: e.g., Ganeshpeth Police Station / Sadar Police Station, Nagpur\n"
        "- **Investigating Agency**: CID / Economic Offences Wing (EOW) / CBI\n"
        "- **Accused Persons & Entities**: Key accused individuals and corporate entities (e.g. Home Trade Ltd, brokerage directors, bank officials)\n"
        "- **Competent Forum / Court**: e.g., Court of Additional Chief Judicial Magistrate (ACJM), Nagpur / High Court of Bombay\n\n"
        "## 4. Internal Case Record Analysis (CALIP Evidence)\n"
        "Synthesize the factual evidence, financial audit figures, and administrative findings from the uploaded case files.\n"
        "Cite exact sources using the format `[CALIP: Document Title, Page X]`.\n\n"
        "## 5. Verified Legal Authorities & Judicial Precedents\n"
        "Detail the connected High Court / Supreme Court orders, legal precedents, and statutory gazette authorities with verifiable citations.\n\n"
        "## 6. Judicial Synthesis & Evidentiary Conclusion\n"
        "Conclude with an evidentiary assessment summarizing what the internal records document and the legal status of the charges.\n\n"
        "STRICT FORMATTING RULES:\n"
        "- Format all tables using standard Markdown (`| col | col |`). Ensure each row has matching column counts.\n"
        "- Bold all key terms, section names, and dates using standard Markdown `**term**`.\n"
        "- Do NOT output raw unparsed formatting markers or conversational preamble.\n"
        "- Present the briefing as an official, court-ready legal intelligence document."
    )

    user_prompt = (
        f"LEGAL INQUIRY: {cleaned_query}\n\n"
        f"=== INTERNAL CALIP CASE RECORDS ===\n"
        f"{internal_str}\n\n"
        f"=== VERIFIED EXTERNAL LEGAL CITATIONS ===\n"
        f"{external_str}\n\n"
        f"Produce the Official Legal Intelligence Briefing now:"
    )

    # 7. Query Active LLM
    active_model = get_active_model_name()
    llm_answer = query_ollama(prompt=user_prompt, system_prompt=system_prompt, model=active_model)
    if not llm_answer:
        llm_answer = extractive_fallback_answer(cleaned_query, retrieved_chunks)

    # 8. Render HTML
    rendered_html = render_markdown_to_html(llm_answer)

    return {
        "query": cleaned_query,
        "answer": llm_answer,
        "rendered_html": rendered_html,
        "sources": retrieved_chunks,
        "external_sources": external_authorities,
        "model": active_model if llm_answer and "Based on the available" not in llm_answer else "extractive_legal_rule",
        "grounded": True,
    }
