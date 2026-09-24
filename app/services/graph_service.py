from __future__ import annotations

import re
from typing import Any
from app.db.session import SessionLocal
from app.db.models import LegalEntity, RelationshipEdge, Case, Document, Section, Act

COURT_PATTERNS = [
    r"(Supreme Court of India|Supreme Court)",
    r"(Bombay High Court|High Court of Bombay|Gujarat High Court|Delhi High Court|Calcutta High Court|High Court)",
    r"(Sessions Court|Magistrate Court|CBI Court|EOW Special Court|MPID Court|District Court)",
]

ACT_PATTERNS = [
    (r"Indian Penal Code|IPC", "Indian Penal Code", 1860),
    (r"Code of Criminal Procedure|Cr\.?P\.?C\.?", "Code of Criminal Procedure", 1973),
    (r"Negotiable Instruments Act|N\.?I\.? Act", "Negotiable Instruments Act", 1881),
    (r"Specific Relief Act", "Specific Relief Act", 1963),
    (r"Companies Act", "Companies Act", 2013),
    (r"Prevention of Corruption Act", "Prevention of Corruption Act", 1988),
    (r"Maharashtra Protection of Interest of Depositors Act|MPID Act", "MPID Act", 1999),
]

SECTION_PATTERN = re.compile(
    r"(?:Section|Sec\.|U/s|u/s|Section\(s\))\s*(?P<section>\d{1,4}[A-Z]?(?:\s*\(\d+\))?)",
    re.IGNORECASE,
)

PRECEDENT_PATTERN = re.compile(
    r"(?P<case_name>[A-Z][a-zA-Z\s.,]+?\s+v(?:s)?\.?\s+[A-Z][a-zA-Z\s.,]+?)(?:,\s*(?P<citation>\d{4}\s+(?:SCC|AIR|SCC OnLine|Cri LJ)[^\n,.]+))?",
)


def extract_entities_from_text(text: str, document_id: str | None = None, page_number: int = 1) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []

    # 1. Courts
    for pattern in COURT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            court_name = match.group(0).strip()
            entities.append({
                "type": "Court",
                "name": court_name,
                "confidence": 0.95,
                "document_id": document_id,
                "page_number": page_number,
            })

    # 2. Acts
    for pattern, canonical_act, year in ACT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            entities.append({
                "type": "Act",
                "name": canonical_act,
                "confidence": 0.98,
                "document_id": document_id,
                "page_number": page_number,
            })

    # 3. Sections
    for match in SECTION_PATTERN.finditer(text):
        sec = match.group("section").strip()
        entities.append({
            "type": "Section",
            "name": f"Section {sec}",
            "confidence": 0.90,
            "document_id": document_id,
            "page_number": page_number,
        })

    # 4. Precedents / Citations
    for match in PRECEDENT_PATTERN.finditer(text):
        c_name = match.group("case_name").strip()
        if len(c_name) > 10 and len(c_name.split()) >= 3:
            entities.append({
                "type": "Precedent",
                "name": c_name,
                "citation": match.group("citation") or "",
                "confidence": 0.85,
                "document_id": document_id,
                "page_number": page_number,
            })

    return entities


def save_extracted_entities_and_relationships(
    case_id: str | None,
    document_id: str,
    entities: list[dict[str, Any]],
) -> int:
    db = SessionLocal()
    edges_created = 0
    added_entity_ids: set[str] = set()
    added_edge_ids: set[str] = set()

    try:
        for ent in entities:
            # Save or get Entity
            ent_id = f"ent_{re.sub(r'[^a-zA-Z0-9]', '_', ent['name'].lower())[:40]}"
            if ent_id not in added_entity_ids:
                existing_ent = db.query(LegalEntity).filter_by(id=ent_id).first()
                if not existing_ent:
                    new_ent = LegalEntity(
                        id=ent_id,
                        entity_type=ent["type"],
                        name=ent["name"],
                        normalized_name=ent["name"].lower(),
                        confidence=ent["confidence"],
                        source_document_id=document_id,
                        page_number=ent.get("page_number", 1),
                    )
                    db.add(new_ent)
                added_entity_ids.add(ent_id)

            # Create Knowledge Graph Edge
            # Document -> contains_entity -> Entity
            edge_id_1 = f"edge_doc_{document_id}_{ent_id}"
            if edge_id_1 not in added_edge_ids:
                if not db.query(RelationshipEdge).filter_by(id=edge_id_1).first():
                    db.add(RelationshipEdge(
                        id=edge_id_1,
                        subject_id=document_id,
                        subject_type="Document",
                        predicate="contains_entity",
                        object_id=ent_id,
                        object_type=ent["type"],
                        confidence=ent["confidence"],
                        source_document_id=document_id,
                        page_number=ent.get("page_number", 1),
                    ))
                    edges_created += 1
                added_edge_ids.add(edge_id_1)

            # Case -> applies/involves -> Entity
            if case_id:
                predicate = "applies" if ent["type"] in ["Act", "Section"] else "involves"
                edge_id_2 = f"edge_case_{case_id}_{ent_id}"
                if edge_id_2 not in added_edge_ids:
                    if not db.query(RelationshipEdge).filter_by(id=edge_id_2).first():
                        db.add(RelationshipEdge(
                            id=edge_id_2,
                            subject_id=case_id,
                            subject_type="Case",
                            predicate=predicate,
                            object_id=ent_id,
                            object_type=ent["type"],
                            confidence=ent["confidence"],
                            source_document_id=document_id,
                            page_number=ent.get("page_number", 1),
                        ))
                        edges_created += 1
                    added_edge_ids.add(edge_id_2)

        db.commit()
    finally:
        db.close()
    return edges_created


def get_case_graph_relationships(case_id: str) -> dict[str, Any]:
    db = SessionLocal()
    try:
        edges = db.query(RelationshipEdge).filter(
            (RelationshipEdge.subject_id == case_id) | (RelationshipEdge.object_id == case_id)
        ).all()

        nodes = set()
        node_details = []
        links = []

        nodes.add(case_id)
        node_details.append({"id": case_id, "label": case_id, "type": "Case"})

        for edge in edges:
            other_id = edge.object_id if edge.subject_id == case_id else edge.subject_id
            other_type = edge.object_type if edge.subject_id == case_id else edge.subject_type
            if other_id not in nodes:
                nodes.add(other_id)
                ent = db.query(LegalEntity).filter_by(id=other_id).first()
                label = ent.name if ent else other_id
                node_details.append({"id": other_id, "label": label, "type": other_type})

            links.append({
                "source": edge.subject_id,
                "target": edge.object_id,
                "predicate": edge.predicate,
                "confidence": edge.confidence,
            })

        return {"nodes": node_details, "links": links}
    finally:
        db.close()
