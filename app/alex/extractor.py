"""
ALEX Entity & Field Extractor.
Extracts Indian legal entities, statutory provisions, accused, evidence,
witnesses, court proceedings, and timeline events with auditable provenance.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Optional

from app.alex.ocr import DocumentLayout, PageLayout, LayoutBlock
from app.alex.provenance import create_provenance_envelope
from app.services.atom_resolver import extract_fir_coordinates

# ==============================================================================
# COMPILED PATTERNS FOR LEGAL ENTITY EXTRACTION
# ==============================================================================

# Statutory Provisions
STATUTE_SECTION_REGEX = re.compile(
    r"(?:u/s|sec\.?|section|sections)\s*([0-9A-Za-z,\s/&()\-]+?)\s*(?:of\s*(?:the\s*)?(?:ipc|indian\s+penal\s+code|bns|cr\.?p\.?c|bnss|mpid|pocso|ndps|it\s+act|arms\s+act|prevention\s+of\s+corruption\s+act|negotiable\s+instruments\s+act|ni\s+act)|(?=[\n.,;]|$))",
    re.IGNORECASE,
)

# Accused patterns
MARKED_ACCUSED_REGEX = re.compile(
    r"\b(?:A-?(\d+)|Accused\s*No\.?\s*(\d+))\s*[:\-–]?\s*([A-Z][a-zA-Z\s.]+?)(?:[\n,;]|s/o|d/o|w/o|aged|r/o|$)",
    re.IGNORECASE,
)

GENERAL_ACCUSED_REGEX = re.compile(
    r"(?:accused|applicant|petitioner|arrested\s+person)\s*(?:no\.?\s*\d+)?\s*[:\-–]?\s*([A-Z][a-zA-Z\s.]+?)(?:[\n,;]|aged|alias|s/o|d/o|w/o|r/o|$)",
    re.IGNORECASE,
)

# Parentage and age
PARENTAGE_REGEX = re.compile(
    r"\b(?:s/o|son\s+of|w/o|wife\s+of|d/o|daughter\s+of)\s*([A-Z][a-zA-Z\s.]+?)(?:[\n,;]|aged|r/o|$)",
    re.IGNORECASE,
)
AGE_REGEX = re.compile(r"\baged?\s*(?:about\s*)?(\d{1,2})\s*(?:years?|yrs?)?\b", re.IGNORECASE)

# Exhibits & Evidence
EXHIBIT_REGEX = re.compile(
    r"\b(Ex\.?\s*[PDMOpdmo]?-?\s*\d+|MO-?\s*\d+|Exh\.?\s*-?\s*\d+|Exhibit\s*(?:No\.?)?\s*\d+)\b",
    re.IGNORECASE,
)
PANCHNAMA_REGEX = re.compile(r"\b(spot\s+panchnama|inquest\s+panchnama|seizure\s+memo|recovery\s+panchnama)\b", re.IGNORECASE)
CERT_65B_REGEX = re.compile(r"\b(65\s*[-–]?\s*B|certificate\s+under\s+section\s*65\s*B)\b", re.IGNORECASE)

# Witnesses
WITNESS_REGEX = re.compile(
    r"\b(PW-?\s*(\d+)|DW-?\s*(\d+)|CW-?\s*(\d+))\s*[:\-–]?\s*([A-Z][a-zA-Z\s.]+?)(?:[\n,;]|deposed|examined|$)",
    re.IGNORECASE,
)

# Bail outcomes
BAIL_REGEX = re.compile(
    r"\b(bail\s+is\s+granted|bail\s+granted|released\s+on\s+bail|bail\s+is\s+rejected|bail\s+rejected|application\s+is\s+dismissed|anticipatory\s+bail\s+granted)\b",
    re.IGNORECASE,
)

# Date formats commonly found in Indian legal records: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, e.g. 14th August 2021
DATE_REGEX = re.compile(
    r"\b(\d{1,2}[-./]\d{1,2}[-./]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{4})\b",
    re.IGNORECASE,
)


def find_quote_block(
    target_text: str, layout: DocumentLayout
) -> tuple[int, int, Optional[tuple[float, float, float, float]], str]:
    """
    Locates the page, block, bbox, and verbatim quote where a target snippet appears.
    Returns (page_number, block_index, bbox, snippet).
    """
    needle = target_text.lower().strip()
    if not needle:
        return (1, 0, None, "")

    for p in layout.pages:
        for b in p.blocks:
            if needle in b.text.lower():
                return (p.page_number, b.block_index, b.bbox, b.text[:250])

    # Fallback to page 1
    return (1, 0, None, target_text[:200])


def extract_legal_entities(
    layout: DocumentLayout,
    document_id: str,
    file_hash: str = "",
    title: str = "",
) -> dict[str, Any]:
    """
    Extracts structured legal entities from a parsed DocumentLayout.
    Returns standardized entities wrapped with provenance envelopes.
    """
    full_text = layout.full_text

    # 1. FIR Coordinates
    fir_coords = extract_fir_coordinates(text=full_text, title=title)
    coords_page, coords_block, coords_bbox, coords_quote = find_quote_block(
        fir_coords.get("police_station") or fir_coords.get("fir_number") or "", layout
    )

    coordinates_envelope = {
        "fir_number": create_provenance_envelope(
            value=fir_coords.get("fir_number"),
            confidence=fir_coords.get("confidence", 0.8),
            document_id=document_id,
            page=coords_page,
            quote=coords_quote,
            block_index=coords_block,
            bbox=coords_bbox,
            file_hash=file_hash,
            extraction_method="REGEX",
        ),
        "fir_year": create_provenance_envelope(
            value=fir_coords.get("fir_year"),
            confidence=fir_coords.get("confidence", 0.8),
            document_id=document_id,
            page=coords_page,
            quote=coords_quote,
            block_index=coords_block,
            bbox=coords_bbox,
            file_hash=file_hash,
            extraction_method="REGEX",
        ),
        "police_station": create_provenance_envelope(
            value=fir_coords.get("police_station"),
            confidence=fir_coords.get("confidence", 0.8),
            document_id=document_id,
            page=coords_page,
            quote=coords_quote,
            block_index=coords_block,
            bbox=coords_bbox,
            file_hash=file_hash,
            extraction_method="REGEX",
        ),
        "district": create_provenance_envelope(
            value=fir_coords.get("district"),
            confidence=fir_coords.get("confidence", 0.8),
            document_id=document_id,
            page=coords_page,
            quote=coords_quote,
            block_index=coords_block,
            bbox=coords_bbox,
            file_hash=file_hash,
            extraction_method="REGEX",
        ),
        "state": create_provenance_envelope(
            value=fir_coords.get("state"),
            confidence=fir_coords.get("confidence", 0.8),
            document_id=document_id,
            page=coords_page,
            quote=coords_quote,
            block_index=coords_block,
            bbox=coords_bbox,
            file_hash=file_hash,
            extraction_method="REGEX",
        ),
    }

    # 2. Statutory Sections
    found_sections = []
    seen_sec = set()
    for match in STATUTE_SECTION_REGEX.finditer(full_text):
        raw = match.group(1).strip()
        tokens = re.findall(r"\b\d{1,4}[A-Za-z]?(?:\s*\(\d+\))?\b", raw)
        for t in tokens:
            cleaned = t.strip()
            if cleaned and cleaned not in seen_sec:
                seen_sec.add(cleaned)
                p_num, b_idx, b_box, quote = find_quote_block(f"{cleaned}", layout)
                statute = "Indian Penal Code"
                if "bns" in full_text[:match.end() + 50].lower():
                    statute = "Bharatiya Nyaya Sanhita, 2023"
                elif "crpc" in full_text[:match.end() + 50].lower():
                    statute = "Code of Criminal Procedure, 1973"
                elif "bnss" in full_text[:match.end() + 50].lower():
                    statute = "Bharatiya Nagarik Suraksha Sanhita, 2023"

                found_sections.append(
                    {
                        "section": cleaned,
                        "statute": statute,
                        "bailable": cleaned in ("323", "341", "504", "506", "417"),
                        "cognizable": cleaned not in ("504", "417"),
                        "provenance": create_provenance_envelope(
                            value=f"{statute} Section {cleaned}",
                            confidence=0.92,
                            document_id=document_id,
                            page=p_num,
                            quote=quote,
                            block_index=b_idx,
                            bbox=b_box,
                            file_hash=file_hash,
                            extraction_method="REGEX",
                        ),
                    }
                )

    # 3. Accused Profiles
    accused_entities = []
    seen_names = set()

    # Marked accused (A-1, Accused No. 1)
    for m in MARKED_ACCUSED_REGEX.finditer(full_text):
        num = m.group(1) or m.group(2) or "1"
        name = m.group(3).strip()
        if len(name) > 3 and name.lower() not in seen_names and not any(k in name.lower() for k in ("state", "police", "court")):
            seen_names.add(name.lower())
            p_num, b_idx, b_box, quote = find_quote_block(name, layout)
            accused_entities.append(
                {
                    "code": f"A{num}",
                    "name": name,
                    "provenance": create_provenance_envelope(
                        value=name,
                        confidence=0.90,
                        document_id=document_id,
                        page=p_num,
                        quote=quote,
                        block_index=b_idx,
                        bbox=b_box,
                        file_hash=file_hash,
                        extraction_method="REGEX",
                    ),
                }
            )

    # General regex if no marked accused found
    if not accused_entities:
        for m in GENERAL_ACCUSED_REGEX.finditer(full_text[:5000]):
            name = m.group(1).strip()
            if (
                len(name) > 3
                and len(name.split()) >= 2
                and name.lower() not in seen_names
                and not any(k in name.lower() for k in ("state", "police", "court", "judge", "cbi", "magistrate"))
            ):
                seen_names.add(name.lower())
                code = f"A{len(accused_entities) + 1}"
                p_num, b_idx, b_box, quote = find_quote_block(name, layout)
                accused_entities.append(
                    {
                        "code": code,
                        "name": name,
                        "provenance": create_provenance_envelope(
                            value=name,
                            confidence=0.85,
                            document_id=document_id,
                            page=p_num,
                            quote=quote,
                            block_index=b_idx,
                            bbox=b_box,
                            file_hash=file_hash,
                            extraction_method="REGEX",
                        ),
                    }
                )

    # 4. Exhibits & Evidence
    evidence_items = []
    seen_exhibits = set()
    for m in EXHIBIT_REGEX.finditer(full_text):
        ex = m.group(1).strip()
        if ex.upper() not in seen_exhibits:
            seen_exhibits.add(ex.upper())
            p_num, b_idx, b_box, quote = find_quote_block(ex, layout)
            evidence_items.append(
                {
                    "exhibit_number": ex,
                    "category": "DOCUMENTARY",
                    "provenance": create_provenance_envelope(
                        value=ex,
                        confidence=0.88,
                        document_id=document_id,
                        page=p_num,
                        quote=quote,
                        block_index=b_idx,
                        bbox=b_box,
                        file_hash=file_hash,
                        extraction_method="REGEX",
                    ),
                }
            )

    # 5. Witnesses
    witness_list = []
    for m in WITNESS_REGEX.finditer(full_text):
        w_code = m.group(1).upper().replace(" ", "")
        w_name = m.group(5).strip()
        p_num, b_idx, b_box, quote = find_quote_block(w_name, layout)
        witness_list.append(
            {
                "code": w_code,
                "name": w_name,
                "provenance": create_provenance_envelope(
                    value=f"{w_code}: {w_name}",
                    confidence=0.88,
                    document_id=document_id,
                    page=p_num,
                    quote=quote,
                    block_index=b_idx,
                    bbox=b_box,
                    file_hash=file_hash,
                    extraction_method="REGEX",
                ),
            }
        )

    # 6. Bail Outcome Detection
    bail_record = None
    bail_match = BAIL_REGEX.search(full_text)
    if bail_match:
        raw_b = bail_match.group(1).strip()
        outcome = "GRANTED" if "granted" in raw_b.lower() else "REJECTED"
        p_num, b_idx, b_box, quote = find_quote_block(raw_b, layout)
        bail_record = {
            "outcome": outcome,
            "provenance": create_provenance_envelope(
                value=outcome,
                confidence=0.90,
                document_id=document_id,
                page=p_num,
                quote=quote,
                block_index=b_idx,
                bbox=b_box,
                file_hash=file_hash,
                extraction_method="REGEX",
            ),
        }

    return {
        "coordinates": coordinates_envelope,
        "sections": found_sections,
        "accused": accused_entities,
        "evidence": evidence_items,
        "witnesses": witness_list,
        "bail": bail_record,
    }
