from __future__ import annotations

import datetime
import re
from typing import Any

# ==============================================================================
# CALIP LEGAL DOCUMENT CLASSIFIER
# Identifies statutory document types from text, layout, and structural markers.
# Never relies on filename alone.
# ==============================================================================

CLASSIFICATION_RULES = [
    # 1. FIR & Initial Police Records
    {
        "type": "FIR",
        "patterns": [
            r"first\s+information\s+report",
            r"form\s+no\.?\s*24\.5\(1\)",
            r"prathama\s+khabar",
            r"u/s\s*154\s*cr\.?p\.?c",
            r"crime\s+detail\s+form",
            r"integrated\s+investigation\s+form",
        ],
        "negative": [r"quashing\s+of\s+fir", r"in\s+the\s+high\s+court", r"bail\s+application"],
        "weight": 0.95,
    },
    {
        "type": "COMPLAINT",
        "patterns": [
            r"written\s+complaint",
            r"complaint\s+under\s+section\s*156\(3\)",
            r"complaint\s+under\s+section\s*200\s*cr\.?p\.?c",
            r"private\s+complaint",
        ],
        "weight": 0.90,
    },
    # 2. Police Reports & Charge Sheets
    {
        "type": "SUPPLEMENTARY_CHARGE_SHEET",
        "patterns": [
            r"supplementary\s+charge\s*sheet",
            r"further\s+report\s+u/s\s*173\(8\)",
            r"puravni\s+doshrop",
            r"additional\s+police\s+report",
        ],
        "weight": 0.95,
    },
    {
        "type": "CHARGE_SHEET",
        "patterns": [
            r"charge\s*sheet",
            r"final\s+report\s+u/s\s*173",
            r"police\s+report\s+under\s+section\s*173",
            r"doshrop\s+patra",
            r"form\s+no\.?\s*5\.3",
        ],
        "negative": [r"split\s+of\s+charge\s*sheet", r"quashing\s+of\s+charge\s*sheet"],
        "weight": 0.92,
    },
    {
        "type": "CLOSURE_REPORT",
        "patterns": [
            r"closure\s+report",
            r"c\s+summary",
            r"b\s+summary",
            r"a\s+summary",
            r"untraced\s+report",
            r"no\s+evidence\s+found",
        ],
        "weight": 0.90,
    },
    # 3. Investigation Events & Seizures
    {
        "type": "PANCHNAMA",
        "patterns": [
            r"panchnama",
            r"panchanama",
            r"spot\s+panchnama",
            r"inquest\s+panchnama",
            r"panch\s+witness",
        ],
        "weight": 0.92,
    },
    {
        "type": "SEIZURE_MEMO",
        "patterns": [
            r"seizure\s+memo",
            r"panchnama\s+of\s+seizure",
            r"inventory\s+of\s+articles\s+seized",
            r"muddemal\s+receipt",
            r"property\s+seizure\s+memo",
        ],
        "weight": 0.92,
    },
    # 4. Remand
    {
        "type": "REMAND_APPLICATION",
        "patterns": [
            r"police\s+custody\s+remand",
            r"remand\s+application",
            r"remand\s+report\s+u/s\s*167",
            r"remand\s+yadi",
        ],
        "weight": 0.90,
    },
    {
        "type": "REMAND_ORDER",
        "patterns": [
            r"remand\s+order",
            r"remanded\s+to\s+police\s+custody",
            r"remanded\s+to\s+magisterial\s+custody",
            r"remanded\s+to\s+judicial\s+custody",
        ],
        "weight": 0.90,
    },
    # 5. Bail Track
    {
        "type": "ANTICIPATORY_BAIL",
        "patterns": [
            r"anticipatory\s+bail",
            r"u/s\s*438\s*cr\.?p\.?c",
            r"section\s*438\s+of\s+the\s+code\s+of\s+criminal\s+procedure",
            r"pre-arrest\s+bail",
        ],
        "weight": 0.95,
    },
    {
        "type": "DEFAULT_BAIL",
        "patterns": [
            r"default\s+bail",
            r"compulsory\s+bail",
            r"167\(2\)\s*cr\.?p\.?c",
            r"section\s*167\(2\)",
            r"statutory\s+bail",
        ],
        "weight": 0.95,
    },
    {
        "type": "BAIL_APPLICATION",
        "patterns": [
            r"bail\s+application",
            r"application\s+for\s+bail",
            r"application\s+under\s+section\s*437",
            r"application\s+under\s+section\s*439",
            r"prayer\s+for\s+grant\s+of\s+bail",
        ],
        "weight": 0.90,
    },
    {
        "type": "BAIL_ORDER",
        "patterns": [
            r"bail\s+is\s+granted",
            r"bail\s+is\s+rejected",
            r"accused\s+be\s+released\s+on\s+bail",
            r"order\s+on\s+bail\s+application",
            r"bail\s+order",
        ],
        "weight": 0.92,
    },
    # 6. Discharge
    {
        "type": "DISCHARGE_APPLICATION",
        "patterns": [
            r"application\s+for\s+discharge",
            r"discharge\s+u/s\s*227",
            r"discharge\s+u/s\s*239",
            r"discharge\s+application",
        ],
        "weight": 0.92,
    },
    {
        "type": "DISCHARGE_ORDER",
        "patterns": [
            r"order\s+on\s+discharge",
            r"accused\s+is\s+discharged",
            r"plea\s+for\s+discharge\s+is\s+rejected",
        ],
        "weight": 0.92,
    },
    # 7. Trial & Roznama
    {
        "type": "CHARGE_FRAMING_ORDER",
        "patterns": [
            r"charges\s+framed",
            r"charge\s+framing\s+order",
            r"plea\s+of\s+accused\s+recorded",
            r"charge\s+u/s\s*228",
            r"form\s+of\s+charge",
        ],
        "weight": 0.92,
    },
    {
        "type": "ROZNAMA",
        "patterns": [
            r"roznama",
            r"daily\s+order\s*sheet",
            r"daily\s+board",
            r"proceedings\s+sheet",
            r"court\s+proceeding\s+sheet",
            r"ndoh",
        ],
        "weight": 0.90,
    },
    # 8. Witness & Testimonies
    {
        "type": "WITNESS_STATEMENT",
        "patterns": [
            r"statement\s+u/s\s*161",
            r"statement\s+under\s+section\s*161\s*cr\.?p\.?c",
            r"statement\s+recorded\s+by\s+police",
        ],
        "weight": 0.92,
    },
    {
        "type": "EXAMINATION_IN_CHIEF",
        "patterns": [
            r"examination-in-chief",
            r"examination\s+in\s+chief",
            r"chief\s+examination",
            r"deposition\s+of\s+pw",
        ],
        "weight": 0.92,
    },
    {
        "type": "CROSS_EXAMINATION",
        "patterns": [
            r"cross-examination",
            r"cross\s+examination\s+by\s+advocate",
            r"cross\s+examined\s+by\s+defence",
        ],
        "weight": 0.92,
    },
    {
        "type": "DEPOSITION",
        "patterns": [
            r"deposition",
            r"witness\s+no\.?\s*\d+",
            r"deposes\s+on\s+oath",
            r"solemnly\s+affirmed",
        ],
        "weight": 0.88,
    },
    # 9. Forensic & Medical Reports
    {
        "type": "FORENSIC_REPORT",
        "patterns": [
            r"forensic\s+science\s+laboratory",
            r"fsl\s+report",
            r"central\s+forensic",
            r"ballistics\s+report",
            r"chemical\s+analyser",
        ],
        "weight": 0.95,
    },
    {
        "type": "DIGITAL_EVIDENCE",
        "patterns": [
            r"section\s*65b",
            r"65-b\s+certificate",
            r"hash\s+value",
            r"call\s+detail\s+records",
            r"cdr\s+analysis",
            r"digital\s+forensic\s+report",
        ],
        "weight": 0.95,
    },
    # 10. High Court Proceedings
    {
        "type": "HIGH_COURT_PETITION",
        "patterns": [
            r"in\s+the\s+high\s+court\s+of\s+judicature",
            r"writ\s+petition\s+no",
            r"criminal\s+application\s+u/s\s*482",
            r"petition\s+under\s+article\s*226",
            r"criminal\s+appeal\s+no\.?.*high\s+court",
        ],
        "weight": 0.92,
    },
    {
        "type": "HIGH_COURT_ORDER",
        "patterns": [
            r"in\s+the\s+high\s+court\s+of",
            r"coram\s*:.*justice",
            r"operative\s+order.*high\s+court",
        ],
        "weight": 0.88,
    },
    {
        "type": "HIGH_COURT_JUDGMENT",
        "patterns": [
            r"high\s+court\s+of\s+judicature",
            r"judgment\s+reserved\s+on",
            r"pronounced\s+on.*high\s+court",
        ],
        "weight": 0.90,
    },
    # 11. Supreme Court Proceedings
    {
        "type": "SUPREME_COURT_PETITION",
        "patterns": [
            r"in\s+the\s+supreme\s+court\s+of\s+india",
            r"special\s+leave\s+petition",
            r"slp\s*\(crl\)",
            r"transfer\s+petition\s*\(crl\)",
            r"article\s*136",
        ],
        "weight": 0.95,
    },
    {
        "type": "SUPREME_COURT_ORDER",
        "patterns": [
            r"supreme\s+court\s+of\s+india.*order",
            r"item\s+no\.?.*court\s+no\.?.*supreme\s+court",
            r"upon\s+hearing\s+the\s+counsel\s+the\s+court\s+made\s+the\s+following",
        ],
        "weight": 0.92,
    },
    {
        "type": "SUPREME_COURT_JUDGMENT",
        "patterns": [
            r"supreme\s+court\s+of\s+india.*judgment",
            r"reportable.*supreme\s+court",
            r"civil\s+appeal\s+no\..*supreme\s+court",
        ],
        "weight": 0.95,
    },
    # 12. Generic Applications & Orders
    {
        "type": "APPLICATION",
        "patterns": [
            r"application\s+on\s+behalf\s+of",
            r"miscellaneous\s+application",
            r"it\s+is\s+prayed\s+that",
        ],
        "weight": 0.75,
    },
    {
        "type": "ORDER",
        "patterns": [
            r"operative\s+order",
            r"order\s+below\s+exhibit",
            r"perused\s+the\s+record.*ordered\s+that",
            r"heard\s+both\s+sides.*order",
        ],
        "weight": 0.80,
    },
    {
        "type": "JUDGMENT",
        "patterns": [
            r"operative\s+judgment",
            r"convicted\s+under\s+section",
            r"acquitted\s+under\s+section",
            r"reasons\s+for\s+judgment",
        ],
        "weight": 0.85,
    },
]


def classify_legal_document(
    text: str,
    title: str = "",
    folder_context: str = "",
    filename: str = "",
) -> dict[str, Any]:
    """
    Classifies a legal document using multi-layer structural text heuristics.
    Never relies only on filename.
    Returns:
      - document_type: str
      - confidence: float
      - source: str
      - classification_method: str
      - classification_timestamp: str
    """
    combined_content = f"{title}\n{folder_context}\n{text[:4000]}".lower()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    best_type = "OTHER"
    best_score = 0.50

    # 1. Folder structure prior (if folder explicitly says FIR, Charge Sheet, Roznama, etc.)
    folder_lower = folder_context.lower()
    if "fir copy" in folder_lower or "fir" in folder_lower:
        best_type = "FIR"
        best_score = 0.85
    elif "charge sheet" in folder_lower:
        best_type = "CHARGE_SHEET"
        best_score = 0.85
    elif "rozkam" in folder_lower or "roznama" in folder_lower:
        best_type = "ROZNAMA"
        best_score = 0.85
    elif "bail" in folder_lower:
        best_type = "BAIL_APPLICATION"
        best_score = 0.80
    elif "witness" in folder_lower or "evidence" in folder_lower:
        best_type = "WITNESS_STATEMENT"
        best_score = 0.80

    # 2. Text Content & Header Pattern Matching
    for rule in CLASSIFICATION_RULES:
        doc_type = rule["type"]
        weight = rule["weight"]
        patterns = rule["patterns"]
        negative = rule.get("negative", [])

        # Check negative patterns
        if any(re.search(neg, combined_content) for neg in negative):
            continue

        matched_count = 0
        for pat in patterns:
            if re.search(pat, combined_content):
                matched_count += 1

        if matched_count > 0:
            score = weight * (0.8 + 0.2 * min(matched_count, 3) / 3)
            if score > best_score:
                best_score = score
                best_type = doc_type

    # Specific refinement for FIR vs Precedent referencing FIR
    if best_type == "FIR" and ("supreme court" in combined_content or "high court" in combined_content):
        if "first information report" not in combined_content[:500]:
            best_type = "PRECEDENT"
            best_score = 0.80

    return {
        "document_type": best_type,
        "confidence": round(min(best_score, 0.99), 2),
        "source": "content_and_layout_ensemble",
        "classification_method": "regex_structural_heading_ensemble",
        "classification_timestamp": now_iso,
    }
