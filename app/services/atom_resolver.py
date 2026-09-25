from __future__ import annotations

import re
import uuid
from typing import Any
from app.db.session import SessionLocal
from app.db.models import Atom, AtomProceeding, AtomReviewQueue, Document


def get_atom_by_id_or_canonical(db, identifier: str) -> Atom | None:
    """
    Safely fetches an Atom by UUID id or canonical_fir_id without PostgreSQL type casting errors.
    Prevents psycopg2.errors.InvalidTextRepresentation when canonical string is queried against UUID column.
    """
    if not identifier:
        return None
    raw_str = str(identifier).strip()
    try:
        val_uuid = uuid.UUID(raw_str)
        return db.query(Atom).filter((Atom.id == val_uuid) | (Atom.canonical_fir_id == raw_str)).first()
    except (ValueError, AttributeError):
        return db.query(Atom).filter(Atom.canonical_fir_id == raw_str).first()


# Jurisdiction and State Mapping Tables
STATE_CODES = {
    "maharashtra": "MH",
    "mumbai": "MH",
    "nagpur": "MH",
    "wardha": "MH",
    "pune": "MH",
    "amravati": "MH",
    "osmanabad": "MH",
    "gujarat": "GJ",
    "surat": "GJ",
    "anand": "GJ",
    "valsad": "GJ",
    "navsari": "GJ",
    "morbi": "GJ",
    "delhi": "DL",
    "new delhi": "DL",
    "west bengal": "WB",
    "kolkata": "WB",
    "alipore": "WB",
    "bhatpara": "WB",
}

KNOWN_POLICE_STATIONS = {
    "nagpur": ("MH", "NAGPUR", "KOTWALI"),
    "wardha": ("MH", "WARDHA", "CITY"),
    "santacruz": ("MH", "MUMBAI", "SANTACRUZ"),
    "eow": ("MH", "MUMBAI", "EOW"),
    "cbi": ("MH", "MUMBAI", "CBI"),
    "osmanabad": ("MH", "OSMANABAD", "CITY"),
    "amravati": ("MH", "AMRAVATI", "CITY"),
    "vishrambag": ("MH", "PUNE", "VISHRAMBAG"),
    "pimpri": ("MH", "PUNE", "PIMPRI"),
    "anand": ("GJ", "ANAND", "TOWN"),
    "udna": ("GJ", "SURAT", "UDHNA"),
    "udhna": ("GJ", "SURAT", "UDHNA"),
    "adajan": ("GJ", "SURAT", "ADAJAN"),
    "umra": ("GJ", "SURAT", "UMRA"),
    "varacha": ("GJ", "SURAT", "VARACHHA"),
    "varachha": ("GJ", "SURAT", "VARACHHA"),
    "valsad": ("GJ", "VALSAD", "TOWN"),
    "gandevi": ("GJ", "NAVSARI", "GANDEVI"),
    "navsari": ("GJ", "NAVSARI", "TOWN"),
    "morbi": ("GJ", "MORBI", "CITY"),
    "patiala house": ("DL", "NEWDELHI", "TILAKMARG"),
    "sarojini nagar": ("DL", "SOUTHDELHI", "SAROJININAGAR"),
    "bhat para": ("WB", "BARRACKPORE", "BHATPARA"),
    "bhatpara": ("WB", "BARRACKPORE", "BHATPARA"),
    "sonar pur": ("WB", "SOUTH24PARGANAS", "SONARPUR"),
    "sonarpur": ("WB", "SOUTH24PARGANAS", "SONARPUR"),
    "alipore": ("WB", "KOLKATA", "ALIPORE"),
}


def sanitize_code(name: str) -> str:
    """Sanitizes strings for canonical legal identifier generation."""
    clean = re.sub(r"[^A-Za-z0-9]", "", name or "").upper()
    return clean or "UNKNOWN"


def generate_canonical_fir_id(
    state: str,
    district: str,
    police_station: str,
    fir_number: str,
    fir_year: int | str,
) -> str:
    """
    Constructs the canonical Legal Cognitive Atom identity:
    {STATE}-{DISTRICT}-{POLICE_STATION}-{FIR_NO:04d}-{YEAR}
    Example: MH-PUNE-SHIVAJINAGAR-0123-2023
    """
    st_clean = (state or "").strip().lower()
    s_code = STATE_CODES.get(st_clean, sanitize_code(state)[:2])
    d_code = sanitize_code(district)[:16]
    ps_code = sanitize_code(police_station)[:20]

    # Clean FIR number
    clean_no = re.sub(r"[^\d]", "", str(fir_number))
    if not clean_no:
        clean_no = sanitize_code(str(fir_number))
    else:
        clean_no = f"{int(clean_no):04d}"

    # Clean Year
    y_str = str(fir_year).strip()
    if len(y_str) == 2:
        y_int = int(y_str)
        y_str = f"20{y_int:02d}" if y_int < 50 else f"19{y_int:02d}"

    return f"{s_code}-{d_code}-{ps_code}-{clean_no}-{y_str}"


def extract_fir_coordinates(text: str, title: str = "") -> dict[str, Any]:
    """
    Extracts State, District, Police Station, FIR Number, and Year from text and title dynamically.
    """
    combined = f"{title}\n{text[:6000]}"

    fir_num = None
    fir_year = None
    state = None
    district = None
    police_station = None

    # 1. Match FIR / Crime No Pattern: e.g. "FIR No. 147/2002", "Crime No. 255/23"
    fir_match = re.search(
        r"(?:fir|crime|cr\.?)\s*(?:no\.?|number)?\s*[:\-]?\s*(?P<num>\d{1,6})\s*/\s*(?P<year>\d{2,4})",
        combined,
        re.IGNORECASE,
    )
    if fir_match:
        fir_num = fir_match.group("num")
        fir_year = fir_match.group("year")

    # Fallback to generic number pattern if in title e.g. "Nagpur (147/2002)"
    if not fir_num:
        title_match = re.search(r"\(?(?P<num>\d{1,6})\s*/\s*(?P<year>\d{2,4})\)?", title)
        if title_match:
            fir_num = title_match.group("num")
            fir_year = title_match.group("year")

    # Standardize Year
    if fir_year:
        if len(fir_year) == 2:
            y = int(fir_year)
            fir_year = 2000 + y if y < 50 else 1900 + y
        else:
            fir_year = int(fir_year)

    # 2. Dynamic regex matching from document text headers
    ps_match = re.search(
        r"(?:police\s+station|p\.?s\.?)\s*[:\-–]\s*([A-Za-z\s]+?)(?:[\n,;]|\bdistrict\b|\bdist\b|$)",
        combined,
        re.IGNORECASE,
    )
    if ps_match:
        cand_ps = ps_match.group(1).strip()
        if 2 < len(cand_ps) < 30:
            police_station = sanitize_code(cand_ps)

    dist_match = re.search(
        r"(?:district|dist\.?)\s*[:\-–]\s*([A-Za-z\s]+?)(?:[\n,;]|\bstate\b|$)",
        combined,
        re.IGNORECASE,
    )
    if dist_match:
        cand_dist = dist_match.group(1).strip()
        if 2 < len(cand_dist) < 30:
            district = sanitize_code(cand_dist)

    state_match = re.search(
        r"(?:state\s+of|state)\s*[:\-–]\s*([A-Za-z\s]+?)(?:[\n,;]|$)",
        combined,
        re.IGNORECASE,
    )
    if state_match:
        cand_st = state_match.group(1).strip().lower()
        if cand_st in STATE_CODES:
            state = STATE_CODES[cand_st]

    # 3. Fallback to known coordinates dictionary if not found in text headers
    lower_comb = combined.lower()
    if not police_station or not district or not state:
        for ps_key, (st, dist, ps) in KNOWN_POLICE_STATIONS.items():
            if ps_key in lower_comb:
                state = state or st
                district = district or dist
                police_station = police_station or ps
                break

    # If state not found, search state list
    if not state:
        for st_name, code in STATE_CODES.items():
            if st_name in lower_comb:
                state = code
                break

    # 4. Extract CNR if present (16-character eCourts alphanumeric CNR)
    cnr_match = re.search(r"\b([A-Z]{4}\d{12})\b", combined)
    cnr = cnr_match.group(1) if cnr_match else None

    # Calculate Confidence
    confidence = 0.50
    if fir_num and fir_year:
        confidence += 0.25
    if police_station:
        confidence += 0.20
    if state and district:
        confidence += 0.05

    return {
        "fir_number": fir_num,
        "fir_year": fir_year,
        "state": state or "MH",
        "district": district or "UNKNOWN",
        "police_station": police_station or "UNKNOWN",
        "cnr": cnr,
        "confidence": round(confidence, 2),
    }


def resolve_document_to_atom(
    document_id: str,
    text: str,
    title: str = "",
    case_context_id: str | None = None,
) -> dict[str, Any]:
    """
    Atom Resolution Engine:
    Determines if a document belongs to an existing Legal Cognitive Atom,
    creates a new Atom if high confidence, or flags for human review.
    Returns:
      - status: MATCHED | CREATED | REVIEW_REQUIRED | CONFLICT
      - atom_id: str | None
      - canonical_fir_id: str | None
      - confidence: float
      - notes: str
    """
    coords = extract_fir_coordinates(text, title)
    fir_num = coords["fir_number"]
    fir_year = coords["fir_year"]
    state = coords["state"]
    district = coords["district"]
    police_station = coords["police_station"]
    cnr = coords["cnr"]

    db = SessionLocal()
    try:
        # Check 1: If document has CNR, check existing proceedings
        if cnr:
            proceeding = db.query(AtomProceeding).filter_by(cnr=cnr).first()
            if proceeding:
                return {
                    "status": "MATCHED",
                    "atom_id": proceeding.atom_id,
                    "canonical_fir_id": proceeding.atom.canonical_fir_id if proceeding.atom else None,
                    "confidence": 0.98,
                    "notes": f"Matched via CNR {cnr} to Proceeding {proceeding.case_number}",
                }

        # Check 2: Check by legacy case context if present (e.g. lt-4 -> MH-NAGPUR-KOTWALI-0147-2002)
        if case_context_id:
            matched_by_case = db.query(Atom).filter_by(legacy_case_id=case_context_id).first()
            if matched_by_case:
                return {
                    "status": "MATCHED",
                    "atom_id": matched_by_case.id,
                    "canonical_fir_id": matched_by_case.canonical_fir_id,
                    "confidence": 0.95,
                    "notes": f"Matched via Case Context {case_context_id}",
                }

        # Check 3: Check FIR Coordinates
        if not fir_num or not fir_year:
            # Cannot resolve FIR coordinates with certainty
            return {
                "status": "REVIEW_REQUIRED",
                "atom_id": None,
                "canonical_fir_id": None,
                "confidence": coords["confidence"],
                "notes": "FIR number or FIR year not found in document text.",
            }

        if police_station == "UNKNOWN":
            # Missing police station violates canonical identity rules -> Queue for review
            queue_item = AtomReviewQueue(
                document_id=document_id,
                review_reason="MISSING_POLICE_STATION",
                detected_data=coords,
                status="PENDING",
            )
            db.add(queue_item)
            db.commit()
            return {
                "status": "REVIEW_REQUIRED",
                "atom_id": None,
                "canonical_fir_id": None,
                "confidence": coords["confidence"],
                "notes": "FIR number exists but Police Station could not be determined with certainty.",
            }

        # Synthesize Canonical FIR ID
        canon_id = generate_canonical_fir_id(state, district, police_station, fir_num, fir_year)

        # Check if canonical atom already exists
        existing_atom = db.query(Atom).filter_by(canonical_fir_id=canon_id).first()
        if existing_atom:
            return {
                "status": "MATCHED",
                "atom_id": existing_atom.id,
                "canonical_fir_id": existing_atom.canonical_fir_id,
                "confidence": 0.99,
                "notes": f"Matched exact Canonical FIR ID: {canon_id}",
            }

        # If high confidence novel FIR -> Create New Atom
        if coords["confidence"] >= 0.85:
            new_atom = Atom(
                canonical_fir_id=canon_id,
                state=state,
                district=district,
                police_station=police_station,
                fir_number=str(fir_num),
                fir_year=fir_year,
                hydration_status="IDENTITY_VERIFIED",
                confidence_score=coords["confidence"],
                legacy_case_id=case_context_id,
            )
            db.add(new_atom)
            db.commit()
            db.refresh(new_atom)
            return {
                "status": "CREATED",
                "atom_id": new_atom.id,
                "canonical_fir_id": new_atom.canonical_fir_id,
                "confidence": coords["confidence"],
                "notes": f"Created new verified Canonical Atom: {canon_id}",
            }

        # Otherwise queue for review
        queue_item = AtomReviewQueue(
            document_id=document_id,
            review_reason="LOW_CONFIDENCE_FIR",
            detected_data=coords,
            status="PENDING",
        )
        db.add(queue_item)
        db.commit()
        return {
            "status": "REVIEW_REQUIRED",
            "atom_id": None,
            "canonical_fir_id": canon_id,
            "confidence": coords["confidence"],
            "notes": "Confidence score below threshold (0.85). Queued for human verification.",
        }

    finally:
        db.close()
