"""
ALEX OCR & Layout Preservation Module.
Extracts digital text and bounding-box layout blocks via PyMuPDF with seamless OCR fallback.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.services.ocr_service import extract_text_and_ocr_pdf


@dataclass
class LayoutBlock:
    page: int
    block_index: int
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1)
    text: str
    block_type: str = "text"  # "text", "table", "image", "header"


@dataclass
class PageLayout:
    page_number: int  # 1-indexed
    width: float
    height: float
    full_text: str
    blocks: list[LayoutBlock] = field(default_factory=list)
    extraction_method: str = "PYMUPDF_DIGITAL"  # or "OCR_FALLBACK"


@dataclass
class DocumentLayout:
    total_pages: int
    full_text: str
    pages: list[PageLayout] = field(default_factory=list)
    has_scanned_pages: bool = False


def extract_layout_and_text(pdf_path: str) -> DocumentLayout:
    """
    Extracts text, page layouts, and bounding boxes from a PDF.
    If a page has negligible digital text (<40 chars), it falls back to
    the OCR engine in ocr_service to preserve scanned legal documents.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    page_layouts: list[PageLayout] = []
    has_scanned = False
    full_text_parts: list[str] = []

    try:
        total_pages = len(doc)
        for p_idx in range(total_pages):
            page_num = p_idx + 1
            page = doc[p_idx]
            rect = page.rect
            width, height = rect.width, rect.height

            # Extract structured blocks from PyMuPDF
            # page.get_text("blocks") returns tuples: (x0, y0, x1, y1, text, block_no, block_type)
            raw_blocks = page.get_text("blocks")
            blocks: list[LayoutBlock] = []
            page_text_chunks: list[str] = []

            for b_idx, b in enumerate(raw_blocks):
                x0, y0, x1, y1, b_text, b_no, b_type = b
                b_cleaned = b_text.strip()
                if not b_cleaned:
                    continue

                b_type_str = "image" if b_type == 1 else "text"
                blocks.append(
                    LayoutBlock(
                        page=page_num,
                        block_index=b_idx,
                        bbox=(round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)),
                        text=b_cleaned,
                        block_type=b_type_str,
                    )
                )
                page_text_chunks.append(b_cleaned)

            combined_page_text = "\n\n".join(page_text_chunks)

            # Check if page is essentially scanned / image-based
            if len(combined_page_text.strip()) < 40 and total_pages <= 30:
                has_scanned = True
                # Fallback to OCR for this document/page
                try:
                    ocr_res = extract_text_and_ocr_pdf(pdf_path)
                    # Find matching page
                    ocr_pages = ocr_res.get("pages", [])
                    matched = next((p for p in ocr_pages if p.get("page_number") == page_num), None)
                    if matched and len(matched.get("page_text", "")) > len(combined_page_text):
                        combined_page_text = matched["page_text"]
                        blocks = [
                            LayoutBlock(
                                page=page_num,
                                block_index=0,
                                bbox=(0.0, 0.0, width, height),
                                text=combined_page_text,
                                block_type="ocr_text",
                            )
                        ]
                        page_layouts.append(
                            PageLayout(
                                page_number=page_num,
                                width=width,
                                height=height,
                                full_text=combined_page_text,
                                blocks=blocks,
                                extraction_method="OCR_FALLBACK",
                            )
                        )
                        full_text_parts.append(combined_page_text)
                        continue
                except Exception as e:
                    print(f"[ALEX OCR] OCR fallback exception on page {page_num}: {e}")

            page_layouts.append(
                PageLayout(
                    page_number=page_num,
                    width=width,
                    height=height,
                    full_text=combined_page_text,
                    blocks=blocks,
                    extraction_method="PYMUPDF_DIGITAL",
                )
            )
            full_text_parts.append(combined_page_text)

    finally:
        doc.close()

    return DocumentLayout(
        total_pages=len(page_layouts),
        full_text="\n\n--- PAGE BREAK ---\n\n".join(full_text_parts),
        pages=page_layouts,
        has_scanned_pages=has_scanned,
    )
