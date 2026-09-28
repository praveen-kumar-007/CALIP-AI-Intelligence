# CALIP Pilot Golden Dataset Specification (v1.0)

## 1. Overview & Purpose
The CALIP Pilot Golden Dataset is the authoritative evaluation benchmark for the **ALEX (Atomic Legal Extraction) v1 Engine** and the **CALIP Atomic Reasoner**.
All data below is dynamically populated from the active PostgreSQL database.

$$\text{1 Verified FIR} = \text{1 Cognitive Atom} = \text{Canonical PIN (State-District-PS-FIRNo-Year)}$$

---

## 2. Dynamic Pilot Case Roster from Database

| # | Canonical PIN | Police Station | District | State | Sections Registered | Verified |
|---|---|---|---|---|---|---|
| 1 | `MH-MUMBAI-SANTACRUZ-0412-2007` | SANTACRUZ | MUMBAI | MH | IPC 420, 406, 34 | Verified |
| 2 | `GJ-SURAT-UMRA-0389-2023` | UMRA | SURAT | GJ | IPC 420, 406, 120B | Verified |
| 3 | `DL-NEWDELHI-TILAKMARG-0480-2023` | TILAKMARG | NEWDELHI | DL | IPC 420, 406, 120B | Verified |
| 4 | `MH-OSMANABAD-CITY-0398-2002` | CITY | OSMANABAD | MH | IPC 406, 409, 420, 120B | Verified |
| 5 | `WB-BARRACKPORE-BHATPARA-0318-2023` | BHATPARA | BARRACKPORE | WB | IPC 420, 406 | Verified |
| 6 | `GJ-SURAT-ADAJAN-0388-2023` | ADAJAN | SURAT | GJ | IPC 420, 406 | Verified |
| 7 | `MH-MUMBAI-CBI-0083-2002` | CBI | MUMBAI | MH | IPC 120B, 420, PC Act Sec 13(2) r/w 13(1)(d) | Verified |
| 8 | `GJ-MORBI-CITY-1545-2003` | CITY | MORBI | GJ | IPC 420, 406 | Verified |
| 9 | `DL-SOUTHDELHI-SAROJININAGAR-0266-2023` | SAROJININAGAR | SOUTHDELHI | DL | IPC 420, 406 | Verified |
| 10 | `MH-PUNE-VISHRAMBAG-0255-2023` | VISHRAMBAG | PUNE | MH | IPC 420, 406, 34 | Verified |
| 11 | `WB-KOLKATA-ALIPORE-0033-2002` | ALIPORE | KOLKATA | WB | IPC 406, 409, 420, 120B | Verified |
| 12 | `GJ-SURAT-UDHNA-0387-2023` | UDHNA | SURAT | GJ | IPC 420, 406 | Verified |
| 13 | `GJ-NAVSARI-TOWN-0399-2023` | TOWN | NAVSARI | GJ | IPC 420, 406 | Verified |
| 14 | `MH-NAGPUR-KOTWALI-0147-2002` | KOTWALI | NAGPUR | MH | IPC 406, 409, 420, 120B | Verified |
| 15 | `MH-AMRAVATI-CITY-0847-2002` | CITY | AMRAVATI | MH | IPC 406, 409, 420 | Verified |
| 16 | `MH-PUNE-PIMPRI-0256-2023` | PIMPRI | PUNE | MH | IPC 420, 406 | Verified |
| 17 | `GJ-NAVSARI-GANDEVI-0396-2023` | GANDEVI | NAVSARI | GJ | IPC 420, 406 | Verified |
| 18 | `WB-SOUTH24PARGANAS-SONARPUR-0000-2023` | SONARPUR | SOUTH24PARGANAS | WB | IPC 420, 406 | Pending |
| 19 | `GJ-ANAND-TOWN-0361-2023` | TOWN | ANAND | GJ | IPC 420, 406, 120B | Verified |
| 20 | `GJ-VALSAD-TOWN-0395-2023` | TOWN | VALSAD | GJ | IPC 420, 406 | Verified |
| 21 | `MH-MUMBAI-SANTACRUZ-0200-2005` | SANTACRUZ | MUMBAI | MH | IPC 420, 467, 468, 471 | Verified |
| 22 | `MH-MUMBAI-EOW-0324-2002` | EOW | MUMBAI | MH | IPC 409, 420, 120B, MPID Act Sec 3 | Verified |
| 23 | `MH-WARDHA-CITY-0573-2002` | CITY | WARDHA | MH | IPC 406, 409, 420, 120B | Verified |
| 24 | `GJ-SURAT-VARACHHA-0390-2023` | VARACHHA | SURAT | GJ | IPC 420, 406 | Verified |

---

## 3. Evaluation Criteria & Benchmark Metrics
- **Statutory Provision Extraction F1:** Evaluated dynamically against registered sections.
- **Accused Person Identifier F1:** Evaluated dynamically against atom accused table.
- **Atom Completeness Score:** Computed across all 25 conceptual layers.
- **Provenance Verifiability:** Calculated from atom provenance records.