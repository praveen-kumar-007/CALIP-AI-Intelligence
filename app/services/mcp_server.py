"""
CALIP Model Context Protocol (MCP) Remote Server
Enables Claude Custom Connectors, ChatGPT, and external autonomous AI agents to connect
directly to CALIP over Streamable HTTP / Server-Sent Events (SSE) / JSON-RPC 2.0.

Provides standard tools:
- search_documents(query, limit=5)
- get_case(case_id)
- list_atoms()
- get_page(document_id, page_number)
- ask_legal_question(question)
"""

from __future__ import annotations

import json
import logging
from typing import Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse

from app.services.legal_data import (
    get_all_cases,
    get_case_by_id,
    get_all_documents,
    get_document_by_id,
    get_platform_statistics,
    resolve_original_pdf_url,
)
from app.services.hydration_engine import get_all_atoms
from app.services.vector_service import vector_search
from app.services.rag_service import ask_legal_question
from app.services.ocr_service import get_extracted_ocr_data

logger = logging.getLogger("calip.mcp")

# MCP Protocol Version supported by Claude Connectors
MCP_PROTOCOL_VERSION = "2024-11-05"

SERVER_INFO = {
    "name": "calip-legal-intelligence",
    "version": "1.0.0",
    "description": "CALIP Official Remote MCP Server for 46 legal cases, 827 documents, 41,397 pages, and 24 FIR atoms.",
}

# Tool specifications conforming to JSON Schema Draft 7 / MCP specification
MCP_TOOLS = [
    {
        "name": "search_documents",
        "description": "Semantic and keyword search over CALIP legal documents and case records. Returns relevant text chunks with document title, page number, case number, court, and score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The legal search query, e.g. 'Home Trade Rs 5 crore certificate', 'FIR atom 24', 'S. G. Trivedi discharge'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5, max: 20)",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_case",
        "description": "Get complete case details, accused, FIR atoms, court dates, orders, and attached documents for a given case ID (e.g. 'lt-4', 'lt-21', 'lt-22').",
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "description": "The case ID or slug, e.g. 'lt-4' (Nagpur / NDCC Bank / Home Trade case)",
                }
            },
            "required": ["case_id"],
        },
    },
    {
        "name": "list_atoms",
        "description": "List all 24 FIR atoms with case title, FIR numbers, statutory sections (IPC, MPID), police stations, and accused persons.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "get_page",
        "description": "Get the verified OCR text and citations of a specific document page.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "The document ID (e.g. 'doc-Documents_1750940257_pdf')",
                },
                "page_number": {
                    "type": "integer",
                    "description": "Page number (1-indexed, e.g. 1)",
                },
            },
            "required": ["document_id", "page_number"],
        },
    },
    {
        "name": "ask_legal_question",
        "description": "Ask a natural language legal question to CALIP's specialized RAG reasoning engine and get an authoritative answer with page-level citations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The legal question to answer based on CALIP repository data.",
                }
            },
            "required": ["question"],
        },
    },
    {
        "name": "get_platform_stats",
        "description": "Get live counts of indexed cases, documents, pages, chunks, and database metrics across CALIP.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def execute_search_documents(arguments: dict[str, Any]) -> str:
    query = arguments.get("query", "").strip()
    if not query:
        return json.dumps({"error": "Query cannot be empty"})

    limit = min(int(arguments.get("limit", 5)), 20)
    results = vector_search(query=query, top_k=limit)

    formatted = []
    for r in results:
        formatted.append({
            "document_id": r.get("document_id"),
            "document_title": r.get("document_title") or r.get("title"),
            "case_id": r.get("case_id"),
            "case_number": r.get("case_number"),
            "court": r.get("court"),
            "page_number": r.get("page_number"),
            "similarity_score": round(float(r.get("score", 0.0)), 4),
            "text": r.get("chunk_text") or r.get("text", ""),
            "citation": f"[CALIP: {r.get('document_title')}, Page {r.get('page_number')} | Case {r.get('case_number')}, {r.get('court')}]",
        })

    return json.dumps({
        "query": query,
        "results_count": len(formatted),
        "results": formatted,
    }, indent=2)


def execute_get_case(arguments: dict[str, Any]) -> str:
    case_id = arguments.get("case_id", "").strip()
    if not case_id:
        return json.dumps({"error": "case_id is required"})

    case = get_case_by_id(case_id)
    if not case:
        return json.dumps({"error": f"Case '{case_id}' not found in database"})

    # Clean documents list
    docs = []
    for d in case.get("documents", [])[:100]:
        docs.append({
            "id": d.get("id"),
            "title": d.get("title"),
            "document_type": d.get("document_type"),
            "page_count": d.get("page_count"),
            "ocr_status": d.get("ocr_status"),
            "url": d.get("url"),
        })

    payload = {
        "id": case.get("id"),
        "case_number": case.get("case_number"),
        "title": case.get("title"),
        "court": case.get("court"),
        "bench": case.get("bench"),
        "status": case.get("status"),
        "case_type": case.get("case_type"),
        "case_year": case.get("case_year"),
        "filing_date": case.get("filing_date"),
        "summary": case.get("summary"),
        "subject": case.get("subject"),
        "source_url": case.get("source_url"),
        "documents_count": len(case.get("documents", [])),
        "documents": docs,
        "linkages": case.get("linkages", {}),
    }
    return json.dumps(payload, indent=2)


def execute_list_atoms(arguments: dict[str, Any]) -> str:
    raw_atoms = get_all_atoms()
    atoms = []
    for a in raw_atoms:
        atoms.append({
            "id": a.get("id"),
            "police_station": a.get("police_station"),
            "fir_number": a.get("fir_number"),
            "fir_year": a.get("fir_year"),
            "jurisdiction": a.get("jurisdiction"),
            "sections_registered": a.get("sections_registered"),
            "charges_registered": a.get("charges_registered"),
            "investigating_agency": a.get("investigating_agency"),
            "status": a.get("status"),
            "canonical_url": f"https://www.calipai.com/atoms/{a.get('id')}",
        })

    return json.dumps({
        "total_atoms": len(atoms),
        "atoms": atoms,
    }, indent=2)


def execute_get_page(arguments: dict[str, Any]) -> str:
    doc_id = arguments.get("document_id", "").strip()
    page_num = int(arguments.get("page_number", 1))

    if not doc_id:
        return json.dumps({"error": "document_id is required"})

    doc = get_document_by_id(doc_id)
    if not doc:
        return json.dumps({"error": f"Document '{doc_id}' not found"})

    ocr_data = get_extracted_ocr_data(doc_id)
    pages = (ocr_data or {}).get("pages", [])

    page_text = ""
    for p in pages:
        if p.get("page_number") == page_num:
            page_text = p.get("text", "")
            break

    if not page_text and pages and 0 <= (page_num - 1) < len(pages):
        page_text = pages[page_num - 1].get("text", "")

    if not page_text and page_num == 1:
        page_text = doc.get("extracted_text") or doc.get("full_text") or ""

    return json.dumps({
        "document_id": doc_id,
        "document_title": doc.get("title"),
        "case_number": doc.get("case_number"),
        "court": doc.get("court"),
        "page_number": page_num,
        "total_pages": doc.get("page_count", len(pages)),
        "text": page_text[:15000],
        "citation": f"[CALIP: {doc.get('title')}, Page {page_num} | Case {doc.get('case_number')}, {doc.get('court')}]",
    }, indent=2)


def execute_ask_legal_question(arguments: dict[str, Any]) -> str:
    question = arguments.get("question", "") or arguments.get("query", "")
    question = question.strip()
    if not question:
        return json.dumps({"error": "Question cannot be empty"})

    res = ask_legal_question(query=question)
    return json.dumps({
        "question": question,
        "answer": res.get("answer"),
        "confidence_score": res.get("confidence_score") or res.get("confidence_percent"),
        "model_used": res.get("model_used") or res.get("model"),
        "citations": res.get("citations", []) or res.get("sources", []),
        "source_chunks_count": len(res.get("sources", []) or res.get("source_chunks", [])),
    }, indent=2)


def execute_get_platform_stats(arguments: dict[str, Any]) -> str:
    stats = get_platform_statistics()
    return json.dumps(stats, indent=2)


# Dispatch map
TOOL_DISPATCH = {
    "search_documents": execute_search_documents,
    "get_case": execute_get_case,
    "list_atoms": execute_list_atoms,
    "get_page": execute_get_page,
    "ask_legal_question": execute_ask_legal_question,
    "get_platform_stats": execute_get_platform_stats,
}


async def handle_mcp_jsonrpc_request(body: dict[str, Any]) -> dict[str, Any]:
    """Handles an incoming JSON-RPC 2.0 MCP request."""
    jsonrpc = body.get("jsonrpc", "2.0")
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    # 1. initialize
    if method == "initialize":
        return {
            "jsonrpc": jsonrpc,
            "id": req_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {
                        "listChanged": False,
                    },
                    "logging": {},
                },
                "serverInfo": SERVER_INFO,
            },
        }

    # 2. notifications/initialized
    if method == "notifications/initialized":
        return {
            "jsonrpc": jsonrpc,
            "result": {},
        }

    # 3. ping
    if method == "ping":
        return {
            "jsonrpc": jsonrpc,
            "id": req_id,
            "result": {},
        }

    # 4. tools/list
    if method == "tools/list":
        return {
            "jsonrpc": jsonrpc,
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS,
            },
        }

    # 5. tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        handler = TOOL_DISPATCH.get(tool_name)
        if not handler:
            return {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found",
                },
            }

        try:
            result_text = handler(tool_args)
            return {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text,
                        }
                    ],
                    "isError": False,
                },
            }
        except Exception as exc:
            logger.exception("Error executing MCP tool %s", tool_name)
            return {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(exc)}),
                        }
                    ],
                    "isError": True,
                },
            }

    # Unknown method
    return {
        "jsonrpc": jsonrpc,
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not implemented",
        },
    }


def render_mcp_discovery_page() -> str:
    """Renders human and AI readable documentation when visiting /mcp via GET."""
    tools_md = []
    for t in MCP_TOOLS:
        props = t["inputSchema"].get("properties", {})
        props_str = ", ".join(f"`{k}`" for k in props.keys()) or "None"
        tools_md.append(f"- **`{t['name']}`**({props_str}): {t['description']}")

    return f"""# CALIP Remote MCP Server (Model Context Protocol)

**Server Name:** `{SERVER_INFO['name']}`
**Version:** `{SERVER_INFO['version']}`
**MCP Protocol Version:** `{MCP_PROTOCOL_VERSION}`
**Status:** Active & Ready for Claude Connectors

---

## How to Connect in Claude

1. In Claude, click your profile or go to **Settings** -> **Connectors** (or **Custom Connectors**).
2. Click **Add Connector**.
3. Set the Connector URL to:
   `https://www.calipai.com/mcp`
   *(or `https://calipai.com/mcp`)*
4. Save and enable the connector.
5. In your chat, ask questions freely! Claude will automatically call the tools below to retrieve exact case records, document citations, and FIR atoms.

---

## Available MCP Tools

{chr(10).join(tools_md)}

---

## Direct Web Fallback (/bundle)

If your Claude account does not have Custom Connectors enabled, use our bite-sized modular text bundles (all strictly under 20,000 words each):
- Directory Index: [https://www.calipai.com/bundle](https://www.calipai.com/bundle)
- Overview Dossier: [https://www.calipai.com/bundle/overview](https://www.calipai.com/bundle/overview)
- FIR Atoms Digest: [https://www.calipai.com/bundle/atoms](https://www.calipai.com/bundle/atoms)
- Court Dates MIS: [https://www.calipai.com/bundle/court-dates](https://www.calipai.com/bundle/court-dates)
- Case lt-4 Bundle: [https://www.calipai.com/bundle/cases/lt-4](https://www.calipai.com/bundle/cases/lt-4)
"""
