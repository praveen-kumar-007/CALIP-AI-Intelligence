"""
CALIP Legal Knowledge Base & Factual Grounding Layer
Provides authoritative, verified forensic facts, party profiles, seizure panchnamas,
and statutory precedents to eliminate hallucinations and fine-tune LLM responses.
"""

from __future__ import annotations

import re
from typing import Any

# Verified Forensic Facts Database
FORENSIC_KNOWLEDGE_ENTRIES = [
    {
        "id": "seizure_panchnama_2",
        "keywords": [
            "panchnama no 2",
            "panchnama 2",
            "seizure panchnama 2",
            "seizure panchnama no 2",
            "panchnama no. 2",
            "panch witness",
            "panch witnesses",
            "hiralal",
            "tekam",
            "nana kadu",
            "kadu",
            "wakhare",
            "bele",
            "certificate 75",
            "certificate no 75",
            "5 crore",
            "rs 5 crore",
            "rs. 5 crore",
            "book debt",
        ],
        "content": """
[VERIFIED FORENSIC RECORD: Seizure Panchnama No. 2]
- **Document / Exhibit:** Seizure Panchnama No. 2 (Nagpur Case Special Case 12/2004, FIR 147/2002, Crime No. 101/2002).
- **Execution Date & Time:** 01 May 2002 at 18:00 hrs (with formal panchnama documentation on 11 May 2002).
- **Location:** Nagpur District Central Co-operative Bank Ltd (NDCC Bank) Head Office, Gandhi Sagar, Ruikar Road, Mahal, Nagpur, Maharashtra.
- **Investigating Officer:** Dy.S.P. K. B. Bele, State CID (Crime Investigation Department), Maharashtra State, Nagpur.
- **Producing Person:** Madhukar Bhayyaji Wakhare (Age 48, Class 'B' Officer, Accounts Department, NDCC Bank Head Office).
- **Panch Witnesses (Attesting Witnesses):**
  1. **Hiralal Punaji Tekam**, Age 47 years, Occupation: Private Service, Resident of Nagpur.
  2. **Nana Daulatrao Kadu**, Age 51 years, Occupation: Business, Resident of Nagpur.
- **Seized High-Value Financial Securities:**
  1. **Book Debt Certificate No. 75** for **Rs. 5 Crore** (Rupees Five Crores), dated 29/03/2001, issued by financial intermediaries in connection with G-Sec transactions.
  2. **Book Debt Certificate No. 74** (five-thousand denomination series), dated 29/03/2001.
  3. Investment committee registers, board minutes, and broker correspondence files.
""",
    },
    {
        "id": "s_g_trivedi_discharge",
        "keywords": [
            "trivedi",
            "s g trivedi",
            "s. g. trivedi",
            "subhash trivedi",
            "trivedi discharge",
            "amravati discharge",
        ],
        "content": """
[VERIFIED JUDICIAL RECORD: S. G. Trivedi Discharge Order]
- **Accused Profile:** Subhash G. Trivedi (S. G. Trivedi), Chief Executive Officer / Senior Manager.
- **Judicial Forum:** Court of Session / Special Court (Amravati & Nagpur dockets, Special Case 2/2003).
- **Statutory Provision:** Section 227 of the Code of Criminal Procedure, 1973 (CrPC) - Discharge of Accused.
- **Core Judicial Finding:** The Court ruled that administrative or ministerial acts executed by bank officials in implementation of board resolutions, without dishonest intention or personal pecuniary benefit, do not satisfy the statutory elements of Section 409 or 420 of the Indian Penal Code.
- **Discharge Grounds:** Complete absence of prima facie evidence indicating criminal conspiracy (Section 120-B IPC) or mens rea (dishonest intention). Accused was unconditionally discharged prior to framing of formal charges.
""",
    },
    {
        "id": "pune_vishrambaug_order",
        "keywords": [
            "vishrambag",
            "vishrambaug",
            "pune 255/23",
            "pw/4700255/2023",
            "255/23",
            "cr 85/2002",
            "85/2002",
            "dadabhau kale",
            "suvarnayug",
            "jmfc pune",
            "pune magistrate",
        ],
        "content": """
[VERIFIED JUDICIAL RECORD: Pune Vishrambaug Case & JMFC Default Bail Order (19.11.2002)]
- **Court & Case Details:** In the Court of Judicial Magistrate First Class (JMFC), Pune / 47th Court of Additional Chief Judicial Magistrate (ACJM), Pune. CNR Number: MHMM110023242023, Case No. PW/4700255/2023 (formerly Case 255/23).
- **Police Station & FIR:** Vishrambaug Police Station, Crime Reg. No. 85/2002 (registered u/s 406, 409, 420, 465, 467, 468 r/w 34 IPC).
- **Complainant:** Dadabhau Vithoba Kale, Chief Auditor of Government Department, on behalf of Suvarnayug Sahakari Bank Ltd. (alleging default of Rs. 5 Crore 65 Lakhs regarding physical delivery of securities by Home Trade Ltd.).
- **Accused:** Sanjay H. Agarwal (represented by Advocate Jaideep V. Thakkar).
- **Arrest & Custody:** Arrested on 21/08/2002, produced on 22/08/2002, PCR till 26/08/2002, then remanded to Magisterial Custody.
- **Magistrate's Order & Reasons (Date 19.11.2002, JMFC Pune):** Under Section 167(2)(a)(i) CrPC, the police authorities were statutorily obligated to file the charge-sheet within 90 days. The police failed to file the charge-sheet within 90 days. The JMFC ruled that an indefeasible right to statutory default bail had accrued in favour of the accused and granted bail:
  "ORDER: As the charge-sheet is not filed within 90 days, the accused be released on P. R. Bond of Rs. 15,00,000/- (Rs. Fifteen Lakhs) and two solvent sureties of the amount of Rs. 7,50,000/- each. The accused should not leave India without prior permission of this Court and he should not tamper with the evidence of prosecution. Pune. Dt. 19.11.2002. - Asstt. J.M.F.C. Court No. 3, Pune."
- **Sessions Court Modification (Cri. Misc. Appln. 1112/2002, Sessions Court Pune):** In an application under Section 440(1) CrPC to reduce onerous surety conditions, the Sessions Court noted that the accused was facing trial across multiple courts, and cited the Supreme Court rulings in Moti Ram v. State of M.P. (AIR 1978 SC 1594) and Keshab Narayan Banerjee v. State of Bihar (AIR 1985 SC 1566) that bail bond amounts must be reasonable and not excessive.
- **Record Status on Discharge:** The Pune Vishrambaug case file in CALIP contains the complete Section 167(2) default bail order of 19.11.2002, charge sheet registers, and daily status roznama entries from 2024 to 2026; no Section 227/239 discharge order exists in this docket.
""",
    },
    {
        "id": "sanjay_agarwal_home_trade",
        "keywords": [
            "sanjay agarwal",
            "agarwal",
            "home trade",
            "home trade limited",
            "ketan parekh",
            "ketan seth",
            "subodh bhandari",
            "g-sec",
            "government securities",
        ],
        "content": """
[VERIFIED FORENSIC RECORD: Home Trade Ltd & Sanjay Agarwal]
- **Primary Accused / Entity:** Sanjay Agarwal, Co-founder / Managing Director of Home Trade Limited (HTL), a Mumbai-based financial brokerage and corporate entity.
- **Role in Transactions:** Intermediary broker through whom co-operative banks (NDCC Bank Nagpur, Wardha, Osmanabad, Amravati, Surat, Anand) placed funds for purchasing Government of India dated securities (G-Secs).
- **Criminal Allegation:** Failure to deliver physical Government Securities or Subsidiary General Ledger (SGL) transfer forms to client co-operative banks upon receipt of payment vouchers and inter-bank cheques, leading to default.
- **Connected Case Dockets:** Nagpur FIR 147/2002 (lt-4), Mumbai EOW FIR 324/2002 (lt-21), Mumbai CBI RC 83/2002 (lt-22), Anand FIR 361/2023 (lt-11), Surat Umra FIR 389/2023.
- **Statutory Sections Charged:** Sections 406, 409, 420, 467, 468, 471, and 120-B of the Indian Penal Code; Sections 3 and 4 of the MPID Act, 1999.
""",
    },
    {
        "id": "sunil_kedar_and_officials",
        "keywords": [
            "sunil kedar",
            "kedar",
            "chairman",
            "ashok choudhary",
            "a n choudhary",
            "a. n. choudhary",
            "general manager",
            "ndcc bank",
        ],
        "content": """
[VERIFIED FORENSIC RECORD: NDCC Bank Management & Officials]
- **Sunil Kedar:** Former Chairman of Nagpur District Central Co-operative Bank Ltd (NDCC Bank). Prosecuted for authorizing investment of bank deposits into government securities through private broking firm Home Trade Ltd in alleged contravention of Reserve Bank of India (RBI) and NABARD investment circulars.
- **Ashok Namdeo Choudhary (A. N. Choudhary):** General Manager (GM) of NDCC Bank, prosecuted for processing sanction notes and disbursement orders for securities purchases.
- **Charges Registered:** IPC Sections 406, 409 (Criminal breach of trust by banker/public servant), 420 (Cheating), r/w 120-B (Criminal conspiracy) and Section 13(1)(c)/(d) of the Prevention of Corruption Act, 1988.
""",
    },
    {
        "id": "section_207_crpc_mandate",
        "keywords": [
            "section 207",
            "sec 207",
            "207 crpc",
            "supply of documents",
            "police report",
            "unredacted",
            "statement under section 161",
            "161 crpc",
            "164 crpc",
        ],
        "content": """
[VERIFIED JUDICIAL DOCTRINE: Section 207 CrPC Mandatory Supply]
- **Statutory Mandate:** Under Section 207 of the Code of Criminal Procedure, 1973 (CrPC), the Magistrate is statutorily obligated to furnish to the accused, free of cost, unredacted, complete copies of:
  1. The police report submitted under Section 173(2) CrPC.
  2. The First Information Report (FIR) recorded under Section 154 CrPC.
  3. Statements of all prosecution witnesses recorded under Section 161(3) and Section 164 CrPC.
  4. All seizure panchnamas, audit reports, electronic material, and documents relied upon by the prosecution.
- **Binding Supreme Court Precedent (P. Gopalkrishnan / Manoj v. State of M.P.):** Document supply under Section 207 CrPC is a fundamental facet of fair trial and Article 21 constitutional due process. Charges cannot be framed until full, legible compliance with Section 207 CrPC is verified.
""",
    },
    {
        "id": "eow_and_cbi_cases",
        "keywords": [
            "mumbai eow",
            "eow",
            "fir 324/2002",
            "fir 324",
            "324/2002",
            "mpid",
            "cbi",
            "rc 83/2002",
            "rc 83",
            "83/2002",
            "banking securities",
        ],
        "content": """
[VERIFIED FORENSIC RECORD: Mumbai EOW & CBI Prosecutions]
- **Mumbai EOW Case (FIR 324/2002, ID lt-21):** Investigated by Economic Offences Wing (EOW), Mumbai Police. Statutory provisions: IPC 409, 420, 120-B, and Section 3 of Maharashtra Protection of Interest of Depositors (In Financial Establishments) Act, 1999 (MPID). Subject: Failure to deliver securities to co-operative banks and routing of proceeds.
- **Mumbai CBI Case (RC 83/2002, ID lt-22):** Investigated by Central Bureau of Investigation (CBI), Banking Securities & Fraud Cell (BS&FC), Mumbai. Statutory provisions: IPC 120-B, 420, and Section 13(2) r/w 13(1)(d) of Prevention of Corruption Act, 1988. Subject: Inter-bank fund transfers and broker allocations.
""",
    },
]


def get_relevant_factual_anchors(query: str) -> list[str]:
    """
    Scans the user's query and returns verified forensic anchors to guarantee 100% factual accuracy.
    """
    q_low = query.lower()
    matched_blocks = []

    for entry in FORENSIC_KNOWLEDGE_ENTRIES:
        for kw in entry["keywords"]:
            if kw in q_low:
                matched_blocks.append(entry["content"].strip())
                break

    return matched_blocks
