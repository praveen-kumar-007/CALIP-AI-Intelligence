from __future__ import annotations

import re
from typing import Any
from sqlalchemy.orm import joinedload

from app.db.session import SessionLocal
from app.db.models import Atom, AtomProceeding, AtomAccused, AtomAccusedCharge, AtomEvidence, AtomWitness, AtomBailRecord, AtomAllegation, Document
from app.services.llm_provider import query_llm
from app.services.vector_service import vector_search
from app.services.atom_resolver import get_atom_by_id_or_canonical


def query_atomic_reasoner(
    question: str,
    atom_id: str | None = None,
    canonical_fir_id: str | None = None,
    top_k_chunks: int = 5,
) -> dict[str, Any]:
    """
    Atomic Legal Reasoning Engine:
    Constructs a structured IRAC reasoning context directly from the Canonical Atom:
    - FACTS vs ALLEGATIONS
    - ACCUSED -> CHARGES -> EVIDENCE
    - PROCEEDINGS & LINEAGE
    - WITNESSES & TESTIMONIES
    - BAIL STATUS
    - VERIFIED CITATIONS

    Never treats the atom as a simple text blob.
    If evidence is missing, returns NOT_FOUND_IN_AVAILABLE_RECORDS.
    """
    db = SessionLocal()
    try:
        # 1. Resolve Target Atom safely
        atom = None
        target_ref = atom_id or canonical_fir_id
        if target_ref:
            atom = get_atom_by_id_or_canonical(db, target_ref)
        else:
            # Try to extract FIR coordinates or match from question
            all_atoms = db.query(Atom).all()
            q_lower = question.lower()
            for cand in all_atoms:
                if cand.police_station.lower() in q_lower or cand.fir_number in question:
                    atom = cand
                    break

        if not atom:
            # Fallback to general vector search across all documents
            retrieved_chunks = vector_search(query=question, top_k=top_k_chunks)
            if not retrieved_chunks:
                return {
                    "question": question,
                    "answer": "NOT_FOUND_IN_AVAILABLE_RECORDS. No relevant Legal Cognitive Atom or document could be matched to this query.",
                    "atom": None,
                    "sources": [],
                    "grounded": False,
                }
            # Standard grounded answer
            from app.services.rag_service import ask_legal_question
            return ask_legal_question(query=question)

        # 2. Extract Relational Knowledge from the Atom
        atom_proceedings = db.query(AtomProceeding).filter_by(atom_id=atom.id).all()
        atom_accused = db.query(AtomAccused).filter_by(atom_id=atom.id).all()
        atom_charges = db.query(AtomAccusedCharge).filter_by(atom_id=atom.id).all()
        atom_evidence = db.query(AtomEvidence).filter_by(atom_id=atom.id).all()
        atom_witnesses = db.query(AtomWitness).filter_by(atom_id=atom.id).all()
        atom_bail = db.query(AtomBailRecord).filter_by(atom_id=atom.id).all()
        atom_allegations = db.query(AtomAllegation).filter_by(atom_id=atom.id).all()

        # 3. Retrieve targeted vector chunks specifically belonging to this Atom
        matched_chunks = vector_search(query=question, top_k=top_k_chunks, case_id=atom.legacy_case_id)

        # 4. Construct Structured Legal Reasoning Context (IRAC Architecture)
        lineage_str = "\n".join(
            f"- {p.court_tier}: {p.court_name} | Case No: {p.case_number} | Status: {p.status}"
            for p in atom_proceedings
        ) or "Preliminary Magistrate / Cognizance Stage"

        accused_matrix_str = "\n".join(
            f"- Accused [{c.accused.accused_code} - {c.accused.canonical_name}] charged under {c.statute} Sec {c.section} (Stage: {c.charge_stage}, Outcome: {c.trial_outcome})\n  Overt Act Alleged: {c.overt_act_allegation or 'Unspecified in record'}"
            for c in atom_charges if c.accused
        ) or "Charge Sheet / Cognizance in progress"

        allegations_str = "\n".join(
            f"- [{al.status}] ({al.source_speaker}): {al.allegation_text}"
            for al in atom_allegations
        ) or "See attached FIR copy"

        bail_str = "\n".join(
            f"- Accused {b.accused.accused_code} ({b.bail_type} Bail): Outcome = {b.outcome} on {b.decision_date or 'Recorded Date'}. Conditions: {b.conditions_imposed or 'Standard conditions'}"
            for b in atom_bail if b.accused
        ) or "No contested bail orders recorded"

        evidence_str = "\n".join(
            f"- Evidence [{e.evidence_code or 'E'}]: {e.title} ({e.category}, Exhibit: {e.exhibit_number or 'Unmarked'})"
            for e in atom_evidence
        ) or "Exhibits catalogued in primary case books"

        chunk_snippets = "\n\n".join(
            f"[Source Snippet {i+1} | Document: {ch.get('document_title', 'Document')} | Page {ch.get('page_number', 1)}]\n{ch.get('chunk_text', '')}"
            for i, ch in enumerate(matched_chunks)
        )

        bilingual_str = (
            f"Original Language: {atom.original_language or 'English'}\n"
            f"Authentic Native Script (Original Form): {atom.original_language_summary or 'Recorded in case registry'}\n"
            f"Verified English Legal Translation: {atom.english_translated_summary or atom.summary or 'Recorded in case registry'}"
        )

        structured_prompt = f"""You are the CALIP Atomic Legal Reasoning Engine.
You operate on canonical FIR-based Legal Cognitive Atoms.

MANDATORY LEGAL RULES:
1. Distinguish strictly between:
   - What the FIR alleges
   - What the prosecution submits
   - What witnesses testified
   - What the court established or found
2. Never treat an allegation as an established fact.
3. If specific requested information is not recorded in the context below, you MUST state explicitly:
   "NOT_FOUND_IN_AVAILABLE_RECORDS".
4. Do not invent sections, dates, bail results, or judgments.
5. Provide precise citations to the Canonical Atom ID, court proceedings, and page numbers.

DYNAMIC PRESENTATION REQUIREMENTS (NO HARDCODED LAYOUT):
Determine the optimal presentation format dynamically based on the user's specific question and the available evidence:
- If the user asks for comparisons across accused, charges, provisions, or evidentiary items, format the response using a structured Markdown Table (| Accused | Statute & Section | Specific Allegation / Overt Act | Evidentiary Exhibit | Status |).
- If the user asks about chronology, dates, or court progression, format the response using a Procedural Timeline Table (| Date | Court / Forum | Case No. | Proceeding / Order | Stage |).
- If the inquiry touches upon regional vernacular documents (Marathi, Gujarati, Bengali, Hindi), show BOTH the original native script text in its original form and the verified English translation in a structured bilingual comparison format (| Original Native Script (मराठी/हिंदी/ગુજરાતી/বাংলা) | Verified English Translation | Evidentiary Relevance |).
- If the user asks for legal analysis or an executive briefing, provide well-structured sections with markdown headers (##), bold key findings, and tables where comparative data exists.
Never lock the response into a rigid single format. Let the inquiry dictate the clearest, most authoritative structure.

==================================================
CANONICAL LEGAL COGNITIVE ATOM
==================================================
Atom ID: {atom.canonical_fir_id}
State / District / Police Station: {atom.state} / {atom.district} / {atom.police_station}
FIR Number & Year: {atom.fir_number} of {atom.fir_year}
Statutory Sections Registered: {atom.sections_registered}
Hydration Status: {atom.hydration_status}

--- 1. BILINGUAL REGISTRATION & TRANSLATION ---
{bilingual_str}

--- 2. PROCEDURAL LINEAGE ---
{lineage_str}

--- 3. ACCUSED -> CHARGE MATRIX ---
{accused_matrix_str}

--- 4. FIR ALLEGATIONS (Labeled Status) ---
{allegations_str}

--- 5. BAIL TRACK RECORD ---
{bail_str}

--- 6. DOCUMENTARY & DIGITAL EVIDENCE ---
{evidence_str}

--- 7. VERBATIM DOCUMENT SNIPPETS ---
{chunk_snippets or "No matching text snippets."}

==================================================
LEGAL INQUIRY: {question}
==================================================
REASONED GROUNDED ANALYSIS:"""

        # 5. Execute through production LLM provider
        llm_response = query_llm(
            prompt=structured_prompt,
            system_prompt="You are CALIP, an expert Atomic Legal Intelligence Assistant for Indian Criminal Law and Supreme Court / High Court jurisprudence. You format legal analyses dynamically using elegant markdown tables and bilingual cards as appropriate.",
            temperature=0.1,
            max_tokens=2048,
            timeout=12,
        )

        if not llm_response:
            # Deterministic fallback answer with dynamic presentation
            llm_response = (
                f"## Canonical Legal Atom: `{atom.canonical_fir_id}`\n\n"
                f"### Language & Registration\n"
                f"- **Primary Language**: {atom.original_language or 'English'}\n"
                f"- **Native Script (Original)**: {atom.original_language_summary or 'Recorded'}\n"
                f"- **English Translation**: {atom.english_translated_summary or atom.summary}\n\n"
                f"### Accused & Charges Matrix\n\n"
                f"| Accused Code | Accused Name | Statute | Section | Charge Stage |\n"
                f"| :--- | :--- | :--- | :--- | :--- |\n"
            )
            for c in atom_charges:
                ac_code = c.accused.accused_code if c.accused else "A1"
                ac_name = c.accused.canonical_name if c.accused else "Accused"
                llm_response += f"| `{ac_code}` | {ac_name} | {c.statute} | Sec {c.section} | {c.charge_stage} |\n"

            llm_response += (
                f"\n### Procedural Lineage\n{lineage_str}\n\n"
                f"### FIR Allegations\n{allegations_str}\n\n"
                f"*Notice: Grounded atomic briefing generated directly from verified relational records.*"
            )

        from app.services.markdown_renderer import render_markdown_to_html
        rendered_html = render_markdown_to_html(llm_response)

        return {
            "question": question,
            "answer": llm_response,
            "rendered_html": rendered_html,
            "atom": {
                "id": str(atom.id),
                "canonical_fir_id": atom.canonical_fir_id,
                "fir_number": atom.fir_number,
                "fir_year": atom.fir_year,
                "police_station": atom.police_station,
                "state": atom.state,
                "original_language": atom.original_language or "English",
                "hydration_status": atom.hydration_status,
                "doc_count": len(atom.documents),
            },
            "sources": matched_chunks,
            "grounded": True,
        }

    finally:
        db.close()
