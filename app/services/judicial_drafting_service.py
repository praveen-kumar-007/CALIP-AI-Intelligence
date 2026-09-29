"""
CALIP Judicial Drafting Engine - Enterprise Legal Pleading & Document Synthesizer
Generates court-ready Indian judicial drafts (Word .docx and PDF .pdf) adhering strictly
to High Court & District Court formatting standards, statutory CrPC provisions, and
binding Supreme Court precedents.
"""

from __future__ import annotations

import os
import uuid
import datetime
import logging
from pathlib import Path
from typing import Any, Optional

try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    docx = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from app.core.config import settings

logger = logging.getLogger("calip.drafting")

DRAFTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "drafts"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


STANDARD_TEMPLATES = {
    "default_bail_167": {
        "title": "Application for Statutory Default Bail under Section 167(2) Cr.P.C.",
        "statute": "Section 167(2) Code of Criminal Procedure, 1973",
        "precedents": [
            "Bikramjit Singh v. State of Punjab, (2020) 10 SCC 616 (Indefeasible right to default bail upon expiry of 60/90 days)",
            "M. Ravindran v. Directorate of Revenue Intelligence, (2021) 2 SCC 485 (Constitutional right under Article 21)",
            "Sanjay Dutt v. State through C.B.I., (1994) 5 SCC 410 (Right accrues immediately on failure to file charge-sheet)",
            "Moti Ram v. State of M.P., AIR 1978 SC 1594 (Bail bond conditions must be reasonable and not excessive)",
        ],
    },
    "discharge_227_239": {
        "title": "Application for Discharge under Section 227 / 239 Cr.P.C.",
        "statute": "Section 227 / 239 Code of Criminal Procedure, 1973",
        "precedents": [
            "Union of India v. Prafulla Kumar Samal, (1979) 3 SCC 4 (Standard of prima facie case; roving enquiry prohibited; grave suspicion required)",
            "Sajjan Kumar v. C.B.I., (2010) 9 SCC 368 (Principles governing discharge at the threshold)",
            "Central Bureau of Investigation v. K. Narayana Rao, (2012) 9 SCC 512 (Absence of mens rea or criminal conspiracy warrants discharge)",
            "Sujit Biswas v. State of Assam, (2013) 12 SCC 406 (Suspicion, however grave, cannot substitute legal proof)",
        ],
    },
    "section_207_compliance": {
        "title": "Petition for Mandatory Compliance under Section 207 Cr.P.C.",
        "statute": "Section 207 Code of Criminal Procedure, 1973",
        "precedents": [
            "P. Gopalkrishnan @ Dileep v. State of Kerala, (2020) 9 SCC 161 (Accused is entitled to complete cloned / unredacted electronic copies)",
            "Manoj & Ors. v. State of Madhya Pradesh, (2023) 2 SCC 353 (Prosecution must disclose all material collected during investigation)",
            "V.K. Sasikala v. State Represented by Superintendent of Police, (2012) 9 SCC 771 (Fair trial mandates disclosure of unmarked documents)",
        ],
    },
    "written_arguments": {
        "title": "Written Arguments / Submissions on Framing of Charge",
        "statute": "Section 227 / 239 / 240 Code of Criminal Procedure, 1973",
        "precedents": [
            "State of Haryana v. Bhajan Lal, 1992 Supp (1) SCC 335 (Parameters where criminal prosecution constitutes abuse of process)",
            "Dalip Kaur v. Jagnar Singh, (2009) 14 SCC 696 (Distinction between pure breach of civil contract and criminal breach of trust)",
        ],
    },
}


def build_judicial_draft_text(
    court_name: str,
    case_number: str,
    police_station: str,
    fir_number: str,
    sections_invoked: str,
    complainant_name: str,
    accused_name: str,
    draft_type: str,
    facts_summary: str,
    grounds: list[str],
    prayer_text: str,
    advocate_name: str = "Advocate for the Applicant / Accused",
    place: str = "Pune / Nagpur",
) -> str:
    """Constructs formal Indian Court Pleading Text."""
    template_info = STANDARD_TEMPLATES.get(draft_type, STANDARD_TEMPLATES["default_bail_167"])
    title = template_info["title"]
    precedents = template_info["precedents"]

    lines = [
        f"IN THE COURT OF {court_name.upper()}",
        f"AT {place.upper()}",
        "",
        f"CASE NO. / PW NO.: {case_number}",
        f"IN VISHRAMBAUG / CRIME REG. NO.: {fir_number}",
        f"POLICE STATION: {police_station.upper()}",
        f"OFFENCES CHARGED: {sections_invoked.upper()}",
        "",
        "--------------------------------------------------------------------------------",
        "STATE OF MAHARASHTRA",
        f"(Through Investigating Officer, {police_station})",
        "                                                               ... PROSECUTION / COMPLAINANT",
        "                             VERSUS",
        f"{accused_name.upper()}",
        "                                                               ... APPLICANT / ACCUSED",
        "--------------------------------------------------------------------------------",
        "",
        f"APPLICATION ON BEHALF OF THE APPLICANT / ACCUSED UNDER {template_info['statute'].upper()}",
        f"FOR {title.upper()}",
        "",
        "MOST RESPECTFULLY SHOWETH:",
        "",
        "1. PRELIMINARY FACTS & JURISDICTION:",
        f"   The Applicant stands arrayed as an accused in Crime Registration No. {fir_number} registered at {police_station} Police Station under {sections_invoked}. The present application is preferred before this Hon'ble Court seeking relief under {template_info['statute']}.",
        "",
        "2. PROSECUTION ALLEGATIONS & FACTUAL CONTEXT:",
        f"   {facts_summary}",
        "",
        "3. GROUNDS FOR RELIEF:",
    ]

    for idx, g in enumerate(grounds, 1):
        lines.append(f"   ({chr(96 + idx)}) {g}")

    lines.extend([
        "",
        "4. BINDING JUDICIAL PRECEDENTS & STATUTORY DOCTRINES:",
        "   The present prayer is squarely covered by authoritative declarations of the Hon'ble Supreme Court of India:",
    ])

    for p in precedents:
        lines.append(f"   • {p}")

    lines.extend([
        "",
        "5. PRAYER:",
        "   In the premises aforesaid, it is most humbly prayed that this Hon'ble Court may graciously be pleased to:",
        f"   {prayer_text}",
        "   And pass such further or other order(s) as this Hon'ble Court may deem fit and proper in the interest of justice.",
        "",
        f"DATED THIS {datetime.date.today().strftime('%dth DAY OF %B, %Y')}.",
        f"PLACE: {place.upper()}",
        "",
        "                                             APPLICANT / ACCUSED",
        "",
        f"                                             THROUGH: {advocate_name}",
        "",
        "--------------------------------------------------------------------------------",
        "                                 VERIFICATION",
        f"I, the Applicant abovenamed, do hereby solemnly state and affirm on oath that the contents of paragraphs 1 to 5 of the accompanying application are true and correct to the best of my personal knowledge, belief, and judicial records, and nothing material has been concealed therefrom.",
        f"Verified at {place} on this {datetime.date.today().strftime('%dth day of %B, %Y')}.",
        "",
        "                                             DEPONENT / APPLICANT",
    ])

    return "\n".join(lines)


def generate_docx_file(full_text: str, filename: str) -> Path:
    """Generates an attorney-standard Word .docx pleading file."""
    filepath = DRAFTS_DIR / filename
    if not docx:
        # Fallback to plain text if python-docx not present
        filepath.with_suffix(".txt").write_text(full_text, encoding="utf-8")
        return filepath.with_suffix(".txt")

    doc = docx.Document()

    # Set page margins to standard legal 1-inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Style heading
    for line in full_text.split("\n"):
        line_s = line.strip()
        if not line_s:
            doc.add_paragraph("")
            continue

        if line_s.startswith("IN THE COURT OF") or line_s.startswith("AT "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line_s)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
        elif line_s.startswith("APPLICATION ON BEHALF") or line_s.startswith("FOR "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line_s)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif line_s.startswith("MOST RESPECTFULLY SHOWETH") or line_s.startswith("PRAYER") or line_s.startswith("VERIFICATION"):
            p = doc.add_paragraph()
            run = p.add_run(line_s)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif line_s.startswith("--------------------------------------------------------------------------------"):
            p = doc.add_paragraph()
            run = p.add_run("―" * 55)
            run.font.name = "Times New Roman"
            run.font.color.rgb = RGBColor(128, 128, 128)
        else:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            p.paragraph_format.line_spacing = 1.25

    doc.save(str(filepath))
    return filepath


def generate_pdf_file(full_text: str, filename: str) -> Path:
    """Generates an attorney-standard court PDF pleading file via PyMuPDF."""
    filepath = DRAFTS_DIR / filename
    if not fitz:
        # Fallback to plain text
        filepath.with_suffix(".txt").write_text(full_text, encoding="utf-8")
        return filepath.with_suffix(".txt")

    pdf_doc = fitz.open()

    page_width, page_height = 595, 842  # A4 in points
    margin = 54  # 0.75 inch margin
    usable_width = page_width - (margin * 2)

    lines = full_text.split("\n")
    y_pos = margin
    page = pdf_doc.new_page(width=page_width, height=page_height)

    for line in lines:
        if y_pos > page_height - margin - 20:
            page = pdf_doc.new_page(width=page_width, height=page_height)
            y_pos = margin

        line_str = line.strip()
        if not line_str:
            y_pos += 12
            continue

        fontsize = 10
        fontname = "helv"
        is_bold = False

        if line_str.startswith("IN THE COURT OF") or line_str.startswith("APPLICATION ON BEHALF"):
            fontsize = 11
            fontname = "hebo"
            is_bold = True
        elif line_str.startswith("1. ") or line_str.startswith("2. ") or line_str.startswith("3. ") or line_str.startswith("4. ") or line_str.startswith("5. "):
            fontsize = 10
            fontname = "hebo"
            is_bold = True
        elif line_str.startswith("MOST RESPECTFULLY") or line_str.startswith("VERIFICATION"):
            fontsize = 11
            fontname = "hebo"
            is_bold = True

        # Wrap long lines
        words = line.split(" ")
        current_line = ""
        for w in words:
            test_line = (current_line + " " + w).strip()
            # Estimate width (~5.5 pts per char at 10pt)
            if len(test_line) * 5.5 > usable_width:
                page.insert_text((margin, y_pos), current_line, fontsize=fontsize, fontname=fontname)
                y_pos += fontsize + 4
                current_line = w
                if y_pos > page_height - margin - 20:
                    page = pdf_doc.new_page(width=page_width, height=page_height)
                    y_pos = margin
            else:
                current_line = test_line

        if current_line:
            page.insert_text((margin, y_pos), current_line, fontsize=fontsize, fontname=fontname)
            y_pos += fontsize + 4

    pdf_doc.save(str(filepath))
    pdf_doc.close()
    return filepath


def create_judicial_pleading(
    court_name: str,
    case_number: str,
    police_station: str,
    fir_number: str,
    sections_invoked: str,
    accused_name: str,
    draft_type: str = "default_bail_167",
    complainant_name: str = "State of Maharashtra",
    facts_summary: str = "The Applicant was remanded to judicial custody and continues to be incarcerated without the investigating agency having completed investigation or filed the police report under Section 173(2) Cr.P.C. within the statutory period.",
    grounds: Optional[list[str]] = None,
    prayer_text: Optional[str] = None,
    advocate_name: str = "Advocate for the Applicant",
    place: str = "Pune",
) -> dict[str, Any]:
    """Generates complete judicial draft with Word .docx and PDF .pdf download links."""
    if grounds is None:
        grounds = [
            f"That under the mandatory command of Section 167(2) Cr.P.C., the police authorities were duty-bound to complete the investigation and submit the charge-sheet within the prescribed period.",
            f"That the statutory period of 90 days has fully lapsed without any charge-sheet having been filed against the Applicant before this Hon'ble Court.",
            f"That as per authoritative judgments of the Hon'ble Supreme Court in Bikramjit Singh and M. Ravindran, an indefeasible right to statutory default bail has accrued in favour of the Applicant, which cannot be defeated by any subsequent event.",
            f"That the Applicant is a permanent resident, undertakes not to flee the course of justice, and is ready and willing to furnish solvent surety to the satisfaction of this Hon'ble Court.",
        ]

    if prayer_text is None:
        prayer_text = (
            f"a) The Applicant / Accused ({accused_name}) be enlarged on statutory default bail under Section 167(2) Cr.P.C. in connection with Crime Reg. No. {fir_number} of {police_station} Police Station;\n"
            f"   b) The bond and surety conditions be fixed in accordance with Section 440 Cr.P.C. and the dictum of Moti Ram v. State of M.P. so as not to be excessive or onerous."
        )

    full_text = build_judicial_draft_text(
        court_name=court_name,
        case_number=case_number,
        police_station=police_station,
        fir_number=fir_number,
        sections_invoked=sections_invoked,
        complainant_name=complainant_name,
        accused_name=accused_name,
        draft_type=draft_type,
        facts_summary=facts_summary,
        grounds=grounds,
        prayer_text=prayer_text,
        advocate_name=advocate_name,
        place=place,
    )

    draft_uuid = uuid.uuid4().hex[:12]
    safe_title = "".join(c for c in draft_type if c.isalnum() or c == "_")
    docx_filename = f"CALIP_Draft_{safe_title}_{draft_uuid}.docx"
    pdf_filename = f"CALIP_Draft_{safe_title}_{draft_uuid}.pdf"

    docx_path = generate_docx_file(full_text, docx_filename)
    pdf_path = generate_pdf_file(full_text, pdf_filename)

    base_url = "https://www.calipai.com"
    return {
        "draft_id": draft_uuid,
        "draft_type": draft_type,
        "title": STANDARD_TEMPLATES.get(draft_type, {}).get("title", "Judicial Pleading"),
        "court": court_name,
        "case_number": case_number,
        "police_station": police_station,
        "fir_number": fir_number,
        "accused": accused_name,
        "docx_download_url": f"{base_url}/api/drafts/{docx_filename}",
        "pdf_download_url": f"{base_url}/api/drafts/{pdf_filename}",
        "full_draft_text": full_text,
        "word_count": len(full_text.split()),
        "citations_relied_upon": STANDARD_TEMPLATES.get(draft_type, {}).get("precedents", []),
    }
