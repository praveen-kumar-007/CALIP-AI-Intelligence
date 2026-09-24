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
)

Base.metadata.create_all(bind=engine)
