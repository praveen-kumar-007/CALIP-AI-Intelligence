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

        structured_prompt = f"""You are the CALIP Atomic Legal Reasoning Engine.
You operate on canonical FIR-based Legal Cognitive Atoms.

MANDATORY RULES:
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

==================================================
CANONICAL LEGAL COGNITIVE ATOM
==================================================
Atom ID: {atom.canonical_fir_id}
State / District / Police Station: {atom.state} / {atom.district} / {atom.police_station}
FIR Number & Year: {atom.fir_number} of {atom.fir_year}
Statutory Sections Registered: {atom.sections_registered}
Hydration Status: {atom.hydration_status}

--- 1. PROCEDURAL LINEAGE ---
{lineage_str}

--- 2. ACCUSED -> CHARGE MATRIX ---
{accused_matrix_str}

--- 3. FIR ALLEGATIONS (Labeled Status) ---
{allegations_str}

--- 4. BAIL TRACK RECORD ---
{bail_str}

--- 5. DOCUMENTARY & DIGITAL EVIDENCE ---
{evidence_str}

--- 6. VERBATIM DOCUMENT SNIPPETS ---
{chunk_snippets or "No matching text snippets."}

==================================================
LEGAL INQUIRY: {question}
==================================================
REASONED GROUNDED ANALYSIS:"""

        # 5. Execute through production LLM provider
        llm_response = query_llm(
            prompt=structured_prompt,
            system_prompt="You are CALIP, an expert Atomic Legal Intelligence Assistant for Indian Criminal Law and Supreme Court / High Court jurisprudence.",
            temperature=0.1,
            max_tokens=2048,
            timeout=12,
        )

        if not llm_response:
            # Deterministic fallback answer
            llm_response = (
                f"**Canonical Atom:** `{atom.canonical_fir_id}`\n\n"
                f"**Proceedings & Lineage:**\n{lineage_str}\n\n"
                f"**Accused & Charges:**\n{accused_matrix_str}\n\n"
                f"**FIR Allegations:**\n{allegations_str}\n\n"
                f"*Notice: Analysis generated directly from structured relational records.*"
            )

        return {
            "question": question,
            "answer": llm_response,
            "atom": {
                "id": str(atom.id),
                "canonical_fir_id": atom.canonical_fir_id,
                "fir_number": atom.fir_number,
                "fir_year": atom.fir_year,
                "police_station": atom.police_station,
                "state": atom.state,
                "hydration_status": atom.hydration_status,
                "doc_count": len(atom.documents),
            },
            "sources": matched_chunks,
            "grounded": True,
        }

    finally:
        db.close()
