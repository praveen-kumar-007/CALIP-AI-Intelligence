"""
CALIP Deterministic Legal Rule Engine.
Purely rule-based, deterministic statutory and procedural checks for Indian criminal cases.
Zero LLM hallucination risk: acts directly on Canonical Atom facts.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RuleEvaluationResult:
    rule_id: str
    rule_name: str
    verdict: str  # "VIOLATION_FLAGGED", "COMPLIANT", "INSUFFICIENT_DATA", "DEFENSE_OPPORTUNITY"
    summary: str
    statutory_basis: str
    precedents: list[str] = field(default_factory=list)
    confidence: float = 1.0
    details: dict[str, Any] = field(default_factory=dict)


# Maximum punishments and limitation categories under IPC / CrPC
# Section -> (max_punishment_years, is_cognizable, is_bailable)
STATUTORY_PENALTIES: dict[str, tuple[float, bool, bool]] = {
    # IPC Offenses
    "420": (7.0, True, False),     # Cheating and dishonestly inducing delivery of property
    "406": (3.0, True, False),     # Criminal breach of trust
    "409": (10.0, True, False),    # Criminal breach of trust by public servant/banker
    "467": (10.0, True, False),    # Forgery of valuable security
    "468": (7.0, True, False),     # Forgery for purpose of cheating
    "471": (7.0, True, False),     # Using as genuine a forged document
    "120B": (7.0, True, False),    # Criminal conspiracy
    "323": (1.0, False, True),     # Voluntarily causing hurt (Limitation: 1 year)
    "324": (3.0, True, False),     # Voluntarily causing hurt by dangerous weapons
    "341": (0.08, True, True),     # Wrongful restraint (1 month -> Limitation: 1 year)
    "342": (1.0, True, True),      # Wrongful confinement (Limitation: 1 year)
    "504": (2.0, False, True),     # Intentional insult with intent to provoke breach of the peace (Limitation: 3 years)
    "506": (2.0, False, True),     # Criminal intimidation (Limitation: 3 years)
    "302": (100.0, True, False),   # Murder (Capital / Life)
    "307": (10.0, True, False),    # Attempt to murder
    "376": (100.0, True, False),   # Rape
    "384": (3.0, True, False),     # Extortion (Limitation: 3 years)
    "392": (10.0, True, False),    # Robbery
    "395": (100.0, True, False),   # Dacoity
    # BNS Equivalent Numbers
    "318(4)": (7.0, True, False),  # BNS Cheating
    "316(2)": (3.0, True, False),  # BNS Criminal breach of trust
    "338": (10.0, True, False),    # BNS Forgery of valuable security
    "336(3)": (7.0, True, False),  # BNS Forgery for purpose of cheating
    "61(2)": (7.0, True, False),   # BNS Criminal conspiracy
}


def parse_date_flexibly(date_str: Optional[str]) -> Optional[datetime.date]:
    """Parses various Indian date formats (DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY)."""
    if not date_str:
        return None
    cleaned = date_str.strip().split()[0].replace(",", "").replace(".", "-").replace("/", "-")
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def evaluate_cheating_ingredients(
    sections: list[str],
    allegations: list[str],
    has_contract: bool = False,
) -> RuleEvaluationResult:
    """
    Evaluates ingredients of Section 420 IPC / Section 318(4) BNS:
    1. Did fraudulent intention exist at the time of inception?
    2. Does the dispute stem from commercial/contractual non-performance?
    """
    has_cheating = any("420" in s or "318(4)" in s or "318" in s for s in sections)
    if not has_cheating:
        return RuleEvaluationResult(
            rule_id="RULE_IPC_420_INGREDIENTS",
            rule_name="Section 420 IPC / 318(4) BNS Cheating Evaluation",
            verdict="INSUFFICIENT_DATA",
            summary="Section 420 IPC / 318(4) BNS is not invoked in this matter.",
            statutory_basis="Section 415 & 420 Indian Penal Code; Section 318 Bharatiya Nyaya Sanhita, 2023",
        )

    allegations_text = " ".join(allegations).lower()
    civil_keywords = [
        "agreement", "contract", "mou", "partnership", "loan", "promissory",
        "cheque", "invoice", "payment", "business transaction", "failed to deliver",
        "breach of contract", "civil suit", "recovery", "dues",
    ]
    inception_keywords = [
        "from the inception", "ab initio", "fraudulent inducement", "fake document",
        "bogus company", "fictitious", "counterfeit", "impersonated",
    ]

    civil_matches = [w for w in civil_keywords if w in allegations_text]
    inception_matches = [w for w in inception_keywords if w in allegations_text]

    if (civil_matches or has_contract) and not inception_matches:
        verdict = "DEFENSE_OPPORTUNITY"
        summary = (
            "Prima facie commercial/civil transaction detected without clear evidence of dishonest intention "
            "at the inception of the contract. Highly amenable to quashing under Section 482 CrPC / Section 528 BNSS."
        )
    elif inception_matches:
        verdict = "COMPLIANT"
        summary = "Allegations explicitly aver fraudulent inducement and deceptive representation at the inception."
    else:
        verdict = "DEFENSE_OPPORTUNITY"
        summary = "Generic cheating allegations; check whether intention to deceive at the inception is pleaded in the FIR."

    return RuleEvaluationResult(
        rule_id="RULE_IPC_420_INGREDIENTS",
        rule_name="Section 420 IPC / 318(4) BNS Cheating Ingredients Evaluation",
        verdict=verdict,
        summary=summary,
        statutory_basis="Sections 415 & 420 IPC / Section 318 BNS",
        precedents=[
            "Uma Shankar Gopalika v. State of Bihar (2005) 10 SCC 336 (Breach of contract does not equal cheating without dishonest inception)",
            "Hridaya Ranjan Prasad Verma v. State of Bihar (2000) 4 SCC 168 (Distinction between breach of contract and criminal cheating)",
            "Sarabjit Kaur v. State of Punjab (2023) 5 SCC 360 (Criminal courts cannot be made tools of civil debt recovery)",
            "Prof. R.K. Vijayasarathy v. Sudha Seetharam (2019) 16 SCC 739 (Abuse of process when purely civil disputes are cloaked with criminal hue)",
        ],
        details={
            "civil_markers_found": civil_matches,
            "inception_markers_found": inception_matches,
            "has_contract": has_contract,
        },
    )


def evaluate_statutory_limitation(
    sections: list[str],
    occurrence_date_str: Optional[str],
    registration_date_str: Optional[str],
) -> RuleEvaluationResult:
    """
    Evaluates Section 468 CrPC / Section 514 BNSS (Bar to taking cognizance after lapse of period of limitation):
    - Offense punishable with fine only: 6 months
    - Offense <= 1 year imprisonment: 1 year
    - Offense 1 to 3 years imprisonment: 3 years
    - Offense > 3 years imprisonment: No limitation bar
    """
    occ_date = parse_date_flexibly(occurrence_date_str)
    reg_date = parse_date_flexibly(registration_date_str)

    if not occ_date or not reg_date:
        return RuleEvaluationResult(
            rule_id="RULE_CRPC_468_LIMITATION",
            rule_name="Section 468 CrPC / Section 514 BNSS Statutory Limitation",
            verdict="INSUFFICIENT_DATA",
            summary="Cannot compute limitation: Occurrence date or Registration date is missing or unparseable.",
            statutory_basis="Section 468 & 469 Code of Criminal Procedure, 1973; Section 514 BNSS, 2023",
        )

    delay_days = (reg_date - occ_date).days
    delay_months = round(delay_days / 30.44, 1)

    # Determine maximum punishment among all sections charged
    max_penalty_years = 0.0
    for sec in sections:
        cleaned_sec = sec.replace("IPC", "").replace("BNS", "").replace("Sec", "").strip()
        penalty = STATUTORY_PENALTIES.get(cleaned_sec)
        if penalty:
            max_penalty_years = max(max_penalty_years, penalty[0])
        elif cleaned_sec in ("420", "467", "468", "471", "302", "307"):
            max_penalty_years = max(max_penalty_years, 7.0)

    # Determine applicable limitation under CrPC 468
    if max_penalty_years > 3.0:
        return RuleEvaluationResult(
            rule_id="RULE_CRPC_468_LIMITATION",
            rule_name="Section 468 CrPC / Section 514 BNSS Statutory Limitation",
            verdict="COMPLIANT",
            summary=(
                f"Offenses charged carry punishment up to {max_penalty_years:.1f} years (> 3 years). "
                f"No statutory limitation bar applies under Section 468 CrPC. (Delay is {delay_days} days)."
            ),
            statutory_basis="Section 468(2) CrPC / Section 514(2) BNSS",
            details={
                "delay_days": delay_days,
                "delay_months": delay_months,
                "max_penalty_years": max_penalty_years,
                "limitation_applicable": False,
            },
        )

    # Offenses with <= 3 years imprisonment
    limitation_limit_months = 36.0 if max_penalty_years > 1.0 else (12.0 if max_penalty_years > 0.0 else 6.0)

    if delay_months > limitation_limit_months:
        verdict = "VIOLATION_FLAGGED"
        summary = (
            f"Bar of limitation applicable! Delay between occurrence and registration is {delay_months:.1f} months "
            f"({delay_days} days), exceeding statutory period of {limitation_limit_months:.0f} months under Section 468 CrPC. "
            f"Cognizance is barred unless delay is formally condoned under Section 473 CrPC."
        )
    else:
        verdict = "COMPLIANT"
        summary = (
            f"Complaint filed within limitation period: {delay_months:.1f} months delay is within the statutory "
            f"limit of {limitation_limit_months:.0f} months under Section 468 CrPC."
        )

    return RuleEvaluationResult(
        rule_id="RULE_CRPC_468_LIMITATION",
        rule_name="Section 468 CrPC / Section 514 BNSS Statutory Limitation",
        verdict=verdict,
        summary=summary,
        statutory_basis="Section 468 Code of Criminal Procedure, 1973; Section 514 BNSS, 2023",
        precedents=[
            "Sarah Mathew v. Institute of Cardio Vascular Diseases (2014) 2 SCC 62 (Relevant date for Section 468 CrPC is date of filing complaint, not date of magistrate taking cognizance)",
            "State of Himachal Pradesh v. Tara Dutt (2000) 1 SCC 230 (Power to condone delay under Section 473 must be exercised judicially and with speaking order)",
        ],
        details={
            "delay_days": delay_days,
            "delay_months": delay_months,
            "limitation_threshold_months": limitation_limit_months,
            "max_penalty_years": max_penalty_years,
            "limitation_applicable": True,
        },
    )


def evaluate_public_servant_sanction(
    accused_descriptions: list[str],
    has_sanction_order: bool = False,
) -> RuleEvaluationResult:
    """
    Evaluates Section 197 CrPC / Section 218 BNSS (Prosecution of Judges and Public Servants):
    No court shall take cognizance of an offense alleged to have been committed by a public servant
    acting or purporting to act in discharge of official duty without prior sanction.
    """
    public_keywords = [
        "police officer", "sub-inspector", "inspector", "constable", "judge",
        "magistrate", "collector", "tehsildar", "government servant", "public servant",
        "officer in-charge", "sho", "revenue officer", "municipal commissioner",
    ]

    matched_keywords = []
    for desc in accused_descriptions:
        desc_lower = desc.lower()
        for kw in public_keywords:
            if kw in desc_lower and kw not in matched_keywords:
                matched_keywords.append(kw)

    if not matched_keywords:
        return RuleEvaluationResult(
            rule_id="RULE_CRPC_197_SANCTION",
            rule_name="Section 197 CrPC / Section 218 BNSS Official Sanction",
            verdict="COMPLIANT",
            summary="None of the accused are identified as public servants acting in official capacity.",
            statutory_basis="Section 197 Code of Criminal Procedure, 1973; Section 218 BNSS, 2023",
        )

    if has_sanction_order:
        verdict = "COMPLIANT"
        summary = f"Public servant involved ({', '.join(matched_keywords)}), and valid sanction under Section 197 CrPC is on record."
    else:
        verdict = "DEFENSE_OPPORTUNITY"
        summary = (
            f"Public servant identified ({', '.join(matched_keywords)}) without proof of Section 197 CrPC sanction. "
            f"Cognizance without prior sanction of the appropriate Government is bad in law if the act was in discharge of duty."
        )

    return RuleEvaluationResult(
        rule_id="RULE_CRPC_197_SANCTION",
        rule_name="Section 197 CrPC / Section 218 BNSS Official Sanction",
        verdict=verdict,
        summary=summary,
        statutory_basis="Section 197 CrPC / Section 218 BNSS",
        precedents=[
            "D. Devaraja v. Owais Sabeer Hussain (2020) 7 SCC 695 (Sanction u/s 197 CrPC is mandatory even at threshold when police officer acted under color of duty)",
            "Indra Devi v. State of Rajasthan (2021) 8 SCC 768 (Sanction is required if there is reasonable connection between act and official duty)",
        ],
        details={
            "matched_keywords": matched_keywords,
            "has_sanction_order": has_sanction_order,
        },
    )


def evaluate_unexplained_fir_delay(
    occurrence_date_str: Optional[str],
    registration_date_str: Optional[str],
    delay_explained_in_fir: bool = False,
) -> RuleEvaluationResult:
    """
    Evaluates FIR delay. While delay is not fatal per se, unexplained delay
    casts serious suspicion and affords strong defense arguments.
    """
    occ_date = parse_date_flexibly(occurrence_date_str)
    reg_date = parse_date_flexibly(registration_date_str)

    if not occ_date or not reg_date:
        return RuleEvaluationResult(
            rule_id="RULE_FIR_DELAY_ASSESSMENT",
            rule_name="FIR Delay & Spontaneity Assessment",
            verdict="INSUFFICIENT_DATA",
            summary="Cannot assess delay: Occurrence date or Registration date missing.",
            statutory_basis="Section 154 Code of Criminal Procedure, 1973",
        )

    delay_days = (reg_date - occ_date).days

    if delay_days <= 1:
        return RuleEvaluationResult(
            rule_id="RULE_FIR_DELAY_ASSESSMENT",
            rule_name="FIR Delay & Spontaneity Assessment",
            verdict="COMPLIANT",
            summary=f"FIR registered promptly ({delay_days} day(s) from occurrence). Spontaneity preserved.",
            statutory_basis="Section 154 CrPC",
            details={"delay_days": delay_days},
        )

    if delay_days > 30 and not delay_explained_in_fir:
        verdict = "DEFENSE_OPPORTUNITY"
        summary = (
            f"Significant unexplained delay of {delay_days} days in lodging FIR. "
            f"Creates strong inference of embellishment, deliberation, and colored version."
        )
    elif delay_days > 7 and not delay_explained_in_fir:
        verdict = "DEFENSE_OPPORTUNITY"
        summary = f"Delay of {delay_days} days in lodging FIR without recorded explanation."
    else:
        verdict = "COMPLIANT"
        summary = f"Delay of {delay_days} days is documented or explained in FIR narrative."

    return RuleEvaluationResult(
        rule_id="RULE_FIR_DELAY_ASSESSMENT",
        rule_name="FIR Delay & Spontaneity Assessment",
        verdict=verdict,
        summary=summary,
        statutory_basis="Section 154 CrPC / Section 173 BNSS",
        precedents=[
            "State of A.P. v. M. Madhusudhan Rao (2008) 15 SCC 582 (Unexplained delay in FIR provides opportunity for concoction)",
            "Thulia Kali v. State of Tamil Nadu (1972) 3 SCC 393 (Delay in lodging FIR often results in embellishment)",
        ],
        details={"delay_days": delay_days, "delay_explained": delay_explained_in_fir},
    )


def run_all_deterministic_rules(
    sections: list[str],
    allegations: list[str],
    occurrence_date: Optional[str] = None,
    registration_date: Optional[str] = None,
    accused_descriptions: Optional[list[str]] = None,
    has_sanction: bool = False,
    has_contract: bool = False,
    delay_explained: bool = False,
) -> list[RuleEvaluationResult]:
    """Runs the suite of deterministic legal checks on an Atom or Case."""
    return [
        evaluate_cheating_ingredients(sections, allegations, has_contract=has_contract),
        evaluate_statutory_limitation(sections, occurrence_date, registration_date),
        evaluate_public_servant_sanction(accused_descriptions or [], has_sanction_order=has_sanction),
        evaluate_unexplained_fir_delay(occurrence_date, registration_date, delay_explained_in_fir=delay_explained),
    ]
