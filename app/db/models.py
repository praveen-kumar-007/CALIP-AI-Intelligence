from __future__ import annotations

import datetime
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
    processing_status = Column(String(32), default="QUEUED", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="documents")
    folder = relationship("LongtailFolder", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, nullable=True)
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
