"""
CALIP Legal Text Sanitizer & Training Data Normalizer
Strips markdown noise (**, __, ***, ###, backticks, stray glyphs),
removes corrupted OCR characters and unprintable control bytes,
normalizes legal typography, punctuation, spacing, and numbers
for optimal Vector DB RAG, downstream LLM reasoning, and model training.
"""

from __future__ import annotations
import re
from typing import Any
import unicodedata


def clean_latin_diacritics(text: str) -> str:
    """Normalizes Latin characters with diacritics (e.g. ü -> u, é -> e) without altering Devanagari or other Indian scripts."""
    def replace_char(match):
        c = match.group(0)
        decomp = unicodedata.normalize('NFKD', c)
        base = ''.join(ch for ch in decomp if not unicodedata.combining(ch))
        return base if base else c
    return re.sub(r'[\u00c0-\u024f]', replace_char, text)


def is_placeholder_or_dummy_text(text: str) -> bool:
    """Detects whether text is an artificial placeholder or docket stub."""
    if not text:
        return True
    s = text.strip().lower()
    if len(s) < 15:
        return True
    patterns = [
        "court docket exhibit",
        "scanned legal record page",
        "scanned judicial record page",
        "text extraction pending",
        "without legible typography",
        "placeholder",
    ]
    for p in patterns:
        if p in s:
            return True
    return False


def sanitize_legal_text_for_rag_and_training(raw_text: str) -> str:
    """
    Cleans raw OCR / model extraction output into clean, meaningful,
    properly structured legal text without markdown asterisks, broken symbols,
    or noise artifacts. Perfect for RAG vector DB retrieval and model fine-tuning.
    """
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Normalize line endings and remove null bytes, zero-width chars, and control characters
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\ufffd\u200b\u200c\u200d\ufeff]", "", text)
    text = clean_latin_diacritics(text)

    # 2. Normalize unicode quotes and dashes
    text = text.replace("“", '"').replace("”", '"').replace("„", '"')
    text = text.replace("‘", "'").replace("’", "'").replace("‚", "'")
    text = text.replace("—", " - ").replace("–", " - ")

    # 3. Normalize bullet points to clean standard dashes or spaces
    text = re.sub(r"^[•·▪►▸⁃■]\s*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"[•·▪►▸⁃■]", " ", text)

    # 4. Strip ALL markdown bold/italic asterisks and formatting markers (**, *, ***, __, `, ###)
    text = re.sub(r"\*{1,6}", "", text)
    text = re.sub(r"_{2,}", " ", text)
    text = re.sub(r"`{1,3}", "", text)
    text = re.sub(r"^[ \t]*#{1,6}\s*", "", text, flags=re.MULTILINE)

    # 5. Remove scanner noise characters and garbage glyphs
    text = re.sub(r"[~^§©®™\\]+", " ", text)
    text = re.sub(r"[-_=]{3,}", " - ", text)

    # 6. Repair broken hyphenated line endings (e.g., "crimi-\nnal" -> "criminal")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # 7. Clean up table pipes and filter markdown alignment lines
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        # Drop markdown table divider lines like |:---|:---| or |--|--| or :-- | :--
        if re.search(r"^\|?[\s:-|]+\|?$", l) and ("-" in l or ":" in l):
            continue
        # Drop lines that are pure dashes or equal signs
        if re.match(r"^[-=_*\s]{2,}$", l):
            continue

        # If line has table pipes, clean cell spacing
        if "|" in l:
            # Check if it's a residual alignment row
            stripped_cells = [c.strip() for c in l.split("|") if c.strip()]
            if all(re.match(r"^[:\s-]+$", c) for c in stripped_cells):
                continue
            cells = [re.sub(r"\s+", " ", c).strip() for c in l.split("|")]
            cells = [c for c in cells if c]
            if cells:
                cleaned_lines.append(" | ".join(cells))
            continue

        # Normal line: compact whitespace
        l = re.sub(r"[ \t]+", " ", l)
        cleaned_lines.append(l)

    text = "\n".join(cleaned_lines)

    # 8. Standardize common abbreviations before general punctuation spacing
    text = re.sub(r"\bp\.\s*a\.", "p.a.", text, flags=re.IGNORECASE)
    text = re.sub(r"\be\.\s*g\.", "e.g.", text, flags=re.IGNORECASE)
    text = re.sub(r"\bi\.\s*e\.", "i.e.", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCr\.?\s*P\.?\s*C\.?", "CrPC", text, flags=re.IGNORECASE)
    text = re.sub(r"\bI\.?\s*P\.?\s*C\.?", "IPC", text, flags=re.IGNORECASE)
    text = re.sub(r"\bC\.?\s*P\.?\s*C\.?", "CPC", text, flags=re.IGNORECASE)
    text = re.sub(r"\bS\.?\s*C\.?\s*R\.?", "SCR", text, flags=re.IGNORECASE)
    text = re.sub(r"\bS\.?\s*C\.?\s*C\.?", "SCC", text, flags=re.IGNORECASE)
    text = re.sub(r"\bA\.?\s*I\.?\s*R\.?", "AIR", text, flags=re.IGNORECASE)

    # 9. Normalize punctuation spacing (no space before comma/period/colon)
    text = re.sub(r"\s+([,.:;?!])", r"\1", text)
    # Ensure space after punctuation only when followed by an uppercase letter or word
    text = re.sub(r"([,;:?!])([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"(\.)([A-Z][a-z])", r"\1 \2", text)

    # 10. Normalize Indian legal citation conventions
    text = re.sub(r"\b[Uu]/[Ss]\b", "u/s", text)
    text = re.sub(r"\b[Rr]/[Ww]\b", "r/w", text)
    text = re.sub(r"\bC\.?R\.?\s*No\.?", "CR No.", text)
    text = re.sub(r"\bF\.?I\.?R\.?\s*No\.?", "FIR No.", text)

    # 11. Final safety check: strip any residual asterisks
    text = text.replace("*", "")

    # 12. Clean multiple consecutive blank lines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text.strip()
