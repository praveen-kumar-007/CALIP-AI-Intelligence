from __future__ import annotations

import datetime
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Court(Base):
    __tablename__ = "courts"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    court_type = Column(String(64), nullable=False, default="District Court")
    jurisdiction = Column(String(128), nullable=True)
    state = Column(String(64), nullable=True, index=True)
    city = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    cases = relationship("Case", back_populates="court_rel")


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(64), primary_key=True, index=True)
    case_number = Column(String(128), nullable=False, index=True)
    case_type = Column(String(64), nullable=True, index=True)
    case_year = Column(Integer, nullable=True, index=True)
    title = Column(String(512), nullable=False, index=True)
    court_name = Column(String(255), nullable=True, index=True)
    court_id = Column(String(64), ForeignKey("courts.id"), nullable=True)
    bench = Column(String(255), nullable=True)
    filing_date = Column(String(32), nullable=True)
    registration_date = Column(String(32), nullable=True)
    status = Column(String(64), default="pending", index=True)
    summary = Column(Text, nullable=True)
    petitioner = Column(Text, nullable=True)
    respondent = Column(Text, nullable=True)
    advocates = Column(Text, nullable=True)
    judges = Column(Text, nullable=True)
    sections = Column(Text, nullable=True)
    acts = Column(Text, nullable=True)
    subject = Column(String(255), nullable=True)
    keywords = Column(Text, nullable=True)
    source_url = Column(String(512), nullable=True)
    canonical_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    court_rel = relationship("Court", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    judgments = relationship("Judgment", back_populates="case", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="case", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="case", cascade="all, delete-orphan")
    folders = relationship("LongtailFolder", back_populates="case", cascade="all, delete-orphan")


class LongtailFolder(Base):
    __tablename__ = "longtail_folders"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=True, index=True)
    parent_id = Column(String(64), ForeignKey("longtail_folders.id"), nullable=True, index=True)
    title = Column(String(512), nullable=False)
    folder_type = Column(String(64), default="folder")  # 'root_case', 'folder', 'subfolder'
    level = Column(Integer, default=1)
    source_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="folders")
    parent = relationship("LongtailFolder", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="folder")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=True, index=True)
    folder_id = Column(String(64), ForeignKey("longtail_folders.id"), nullable=True, index=True)
    document_type = Column(String(64), default="Document", index=True)  # Judgment, Order, Application, FIR, ChargeSheet, Roznama, etc.
    title = Column(String(512), nullable=False, index=True)
    document_number = Column(String(128), nullable=True)
    document_date = Column(String(32), nullable=True)
    court = Column(String(255), nullable=True)
    source_url = Column(String(512), nullable=True)
    original_pdf_url = Column(String(512), nullable=True)
    local_pdf_path = Column(String(512), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256
    page_count = Column(Integer, default=0)
    language = Column(String(32), default="en")
    ocr_required = Column(Boolean, default=False)
    ocr_status = Column(String(32), default="pending")  # completed, not_required, failed
    ocr_confidence = Column(Float, nullable=True)
    extraction_method = Column(String(64), default="pymupdf_text")  # pymupdf_text, my_ocr, tesseract, ollama_vision
    extracted_text = Column(Text, nullable=True)
    original_language_text = Column(Text, nullable=True)  # Genuine local language text (Marathi / Hindi / Gujarati etc.)
    english_translated_text = Column(Text, nullable=True)  # Authoritative English legal draft
    detected_language = Column(String(32), default="English")  # e.g. "Marathi (मराठी)", "Hindi (हिन्दी)", "English"
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=True, index=True)
    processing_status = Column(String(32), default="QUEUED", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="documents")
    atom = relationship("Atom", back_populates="documents")
    folder = relationship("LongtailFolder", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, nullable=True)
    original_page_text = Column(Text, nullable=True)  # Genuine native language page text
    english_page_text = Column(Text, nullable=True)  # Verified English legal page text
    has_images = Column(Boolean, default=False)
    ocr_confidence = Column(Float, nullable=True)
    extraction_method = Column(String(64), default="pymupdf_text")

    document = relationship("Document", back_populates="pages")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    case_id = Column(String(64), nullable=True, index=True)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    section_title = Column(String(255), nullable=True)
    token_count = Column(Integer, default=0)
    embedding = Column(JSON, nullable=True)  # List of floats for vector search
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class Judgment(Base):
    __tablename__ = "judgments"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    title = Column(String(512), nullable=False)
    date = Column(String(32), nullable=True, index=True)
    court = Column(String(255), nullable=True)
    bench = Column(String(255), nullable=True)
    judges = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    issues = Column(Text, nullable=True)
    arguments = Column(Text, nullable=True)
    findings = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    decision = Column(Text, nullable=True)
    directions = Column(Text, nullable=True)
    sections = Column(Text, nullable=True)
    precedents = Column(Text, nullable=True)

    case = relationship("Case", back_populates="judgments")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    order_date = Column(String(32), nullable=True, index=True)
    court = Column(String(255), nullable=True)
    bench = Column(String(255), nullable=True)
    order_type = Column(String(64), default="Interim Order", index=True)
    summary = Column(Text, nullable=True)
    directions = Column(Text, nullable=True)

    case = relationship("Case", back_populates="orders")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(64), primary_key=True, index=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    title = Column(String(512), nullable=False)
    application_type = Column(String(64), default="Application")
    applicant = Column(String(255), nullable=True)
    filing_date = Column(String(32), nullable=True)
    prayer = Column(Text, nullable=True)
    status = Column(String(64), default="Pending")

    case = relationship("Case", back_populates="applications")


class Act(Base):
    __tablename__ = "acts"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    short_code = Column(String(64), nullable=True, index=True)
    year = Column(Integer, nullable=True)
    category = Column(String(128), default="General Law")

    sections = relationship("Section", back_populates="act", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(String(64), primary_key=True, index=True)
    act_id = Column(String(64), ForeignKey("acts.id"), nullable=False)
    section_number = Column(String(32), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    act = relationship("Act", back_populates="sections")


class LegalEntity(Base):
    __tablename__ = "legal_entities"

    id = Column(String(64), primary_key=True, index=True)
    entity_type = Column(String(64), nullable=False, index=True)  # Court, Judge, Advocate, Party, Act, Section
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False)
    confidence = Column(Float, default=1.0)
    source_document_id = Column(String(64), nullable=True)
    page_number = Column(Integer, nullable=True)


class RelationshipEdge(Base):
    __tablename__ = "relationship_edges"

    id = Column(String(64), primary_key=True, index=True)
    subject_id = Column(String(64), nullable=False, index=True)
    subject_type = Column(String(64), nullable=False)
    predicate = Column(String(64), nullable=False, index=True)  # filed_in, has_judge, cites, applies, contains_pdf, etc.
    object_id = Column(String(64), nullable=False, index=True)
    object_type = Column(String(64), nullable=False)
    confidence = Column(Float, default=1.0)
    source_document_id = Column(String(64), nullable=True)
    page_number = Column(Integer, nullable=True)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), nullable=True, index=True)
    stage = Column(String(64), nullable=False)  # QUEUED, DOWNLOADING, EXTRACTING, OCR, CHUNKING, EMBEDDING, GRAPH_UPDATE, PUBLISHED, FAILED
    status = Column(String(32), default="QUEUED", index=True)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# ==============================================================================
# CALIP ATOMIC LEGAL INTELLIGENCE MODELS (ONE VERIFIED FIR = ONE COGNITIVE ATOM)
# ==============================================================================

class Atom(Base):
    __tablename__ = "atoms"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    canonical_fir_id = Column(String(128), unique=True, nullable=False, index=True)
    state = Column(String(64), nullable=False, index=True)
    district = Column(String(64), nullable=False, index=True)
    police_station = Column(String(128), nullable=False, index=True)
    fir_number = Column(String(64), nullable=False, index=True)
    fir_year = Column(Integer, nullable=False, index=True)
    jurisdiction = Column(String(255), nullable=True)
    registration_date = Column(String(32), nullable=True)
    occurrence_date = Column(String(32), nullable=True)
    occurrence_time = Column(String(32), nullable=True)
    place_of_occurrence = Column(Text, nullable=True)
    informant_name = Column(String(255), nullable=True)
    complainant_name = Column(String(255), nullable=True)
    sections_registered = Column(Text, nullable=True)
    original_language = Column(String(32), default="English")
    zero_fir = Column(Boolean, default=False)
    cross_fir_id = Column(String(128), nullable=True)
    counter_fir_id = Column(String(128), nullable=True)
    summary = Column(Text, nullable=True)
    hydration_status = Column(String(64), default="DISCOVERED", index=True)
    confidence_score = Column(Float, default=1.0)
    is_verified = Column(Boolean, default=False, index=True)
    verified_by = Column(String(128), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    legacy_case_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="atom")
    proceedings = relationship("AtomProceeding", back_populates="atom", cascade="all, delete-orphan")
    accused = relationship("AtomAccused", back_populates="atom", cascade="all, delete-orphan")
    charges = relationship("AtomAccusedCharge", back_populates="atom", cascade="all, delete-orphan")
    evidence = relationship("AtomEvidence", back_populates="atom", cascade="all, delete-orphan")
    witnesses = relationship("AtomWitness", back_populates="atom", cascade="all, delete-orphan")
    bail_records = relationship("AtomBailRecord", back_populates="atom", cascade="all, delete-orphan")
    allegations = relationship("AtomAllegation", back_populates="atom", cascade="all, delete-orphan")
    provenance = relationship("AtomProvenance", back_populates="atom", cascade="all, delete-orphan")


class AtomProceeding(Base):
    __tablename__ = "atom_proceedings"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    court_tier = Column(String(64), nullable=False)  # MAGISTRATE, SESSIONS, SPECIAL_COURT, HIGH_COURT, SUPREME_COURT
    court_name = Column(String(255), nullable=False)
    case_number = Column(String(128), nullable=False, index=True)
    case_year = Column(Integer, nullable=True)
    cnr = Column(String(32), nullable=True, index=True)
    presiding_judge = Column(String(255), nullable=True)
    bench = Column(String(255), nullable=True)
    status = Column(String(64), default="PENDING")
    filing_date = Column(String(32), nullable=True)
    disposal_date = Column(String(32), nullable=True)
    parent_proceeding_id = Column(String(64), ForeignKey("atom_proceedings.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="proceedings")


class AtomAccused(Base):
    __tablename__ = "atom_accused"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    accused_code = Column(String(16), nullable=False)  # A1, A2, A3
    canonical_name = Column(String(255), nullable=False, index=True)
    aliases = Column(JSON, default=list)
    custody_status = Column(String(64), default="UNKNOWN")  # IN_CUSTODY, BAIL_GRANTED, ABSCONDING, DISCHARGED
    custody_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="accused")
    charges = relationship("AtomAccusedCharge", back_populates="accused", cascade="all, delete-orphan")
    bail_records = relationship("AtomBailRecord", back_populates="accused", cascade="all, delete-orphan")


class AtomAccusedCharge(Base):
    __tablename__ = "atom_accused_charges"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    accused_id = Column(String(64), ForeignKey("atom_accused.id"), nullable=False, index=True)
    statute = Column(String(128), default="Indian Penal Code")
    section = Column(String(64), nullable=False, index=True)  # 420, 409, 120B
    overt_act_allegation = Column(Text, nullable=True)
    charge_stage = Column(String(64), default="FIR_STAGE")  # FIR_STAGE, CHARGE_SHEET, CHARGES_FRAMED, CONVICTED, ACQUITTED
    trial_outcome = Column(String(64), default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="charges")
    accused = relationship("AtomAccused", back_populates="charges")


class AtomEvidence(Base):
    __tablename__ = "atom_evidence"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    evidence_code = Column(String(32), nullable=True)  # E1, E2, E3
    category = Column(String(64), nullable=False)  # DOCUMENTARY, DIGITAL, FORENSIC, MATERIAL
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    exhibit_number = Column(String(64), nullable=True)  # Ex.P-1, Ex.D-1
    custodian = Column(String(255), nullable=True)
    source_document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    page_number = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    admissibility_status = Column(String(64), default="ADMISSIBLE")
    proves_proposition = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="evidence")


class AtomWitness(Base):
    __tablename__ = "atom_witnesses"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    witness_code = Column(String(32), nullable=False)  # PW-1, PW-2, DW-1
    witness_name = Column(String(255), nullable=False)
    witness_role = Column(String(128), default="EYEWITNESS")
    statement_161_summary = Column(Text, nullable=True)
    deposition_summary = Column(Text, nullable=True)
    contradictions_recorded = Column(Text, nullable=True)
    is_hostile = Column(Boolean, default=False)
    source_document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="witnesses")


class AtomBailRecord(Base):
    __tablename__ = "atom_bail_records"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    accused_id = Column(String(64), ForeignKey("atom_accused.id"), nullable=False, index=True)
    proceeding_id = Column(String(64), ForeignKey("atom_proceedings.id"), nullable=True)
    bail_type = Column(String(64), nullable=False)  # REGULAR, ANTICIPATORY, DEFAULT, INTERIM
    application_date = Column(String(32), nullable=True)
    decision_date = Column(String(32), nullable=True)
    outcome = Column(String(64), nullable=False)  # GRANTED, REJECTED, WITHDRAWN, PENDING
    grounds_urged = Column(Text, nullable=True)
    prosecution_objections = Column(Text, nullable=True)
    conditions_imposed = Column(Text, nullable=True)
    source_document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="bail_records")
    accused = relationship("AtomAccused", back_populates="bail_records")


class AtomAllegation(Base):
    __tablename__ = "atom_allegations"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    allegation_text = Column(Text, nullable=False)
    status = Column(String(64), default="ALLEGED")  # ALLEGED, TESTIFIED, SUBMITTED, ESTABLISHED, DISPUTED, REJECTED
    source_speaker = Column(String(128), default="INFORMANT")
    source_document_id = Column(String(64), ForeignKey("documents.id"), nullable=True)
    page_number = Column(Integer, nullable=True)
    paragraph_number = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="allegations")


class AtomProvenance(Base):
    __tablename__ = "atom_provenance"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    target_table = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=False)
    target_field = Column(String(64), nullable=False)
    source_document_id = Column(String(64), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=True)
    paragraph_number = Column(Integer, nullable=True)
    verbatim_quote = Column(Text, nullable=True)
    confidence_score = Column(Float, default=1.0)
    extraction_method = Column(String(64), nullable=True)
    is_human_verified = Column(Boolean, default=False)
    verified_by = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    atom = relationship("Atom", back_populates="provenance")


class AtomReviewQueue(Base):
    __tablename__ = "atom_review_queue"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False)
    atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=True)
    review_reason = Column(String(128), nullable=False)
    detected_data = Column(JSON, default=dict)
    status = Column(String(32), default="PENDING", index=True)
    assigned_to = Column(String(128), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class AtomLink(Base):
    __tablename__ = "atom_links"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    source_atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False)  # same_transaction, cross_fir, counter_fir, companion_case
    target_atom_id = Column(String(64), ForeignKey("atoms.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
