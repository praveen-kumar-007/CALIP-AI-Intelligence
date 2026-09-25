import os
from app.db.session import Base, SessionLocal, engine, get_db
from app.db.models import (
    Case,
    Document,
    DocumentPage,
    DocumentChunk,
    Judgment,
    Order,
    Application,
    Court,
    Act,
    Section,
    LegalEntity,
    RelationshipEdge,
    LongtailFolder,
    ProcessingJob,
    Atom,
    AtomProceeding,
    AtomAccused,
    AtomReviewQueue,
)


def init_db():
    """Initializes tables on demand (for local development or setup scripts only)."""
    Base.metadata.create_all(bind=engine)

