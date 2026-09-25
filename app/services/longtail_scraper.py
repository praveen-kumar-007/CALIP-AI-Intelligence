from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import Case, Court, Document, LongtailFolder, RelationshipEdge

BASE_URL = settings.LONGTAIL_BASE_URL
HEADERS = {"User-Agent": settings.SCRAPER_USER_AGENT}
_CATALOG_CACHE: dict[str, Any] = {}

CASE_PATTERN = re.compile(
    r"(?P<court>[^()\n]+?)\s*(?:\((?P<case_number>[\w/ -]+)\))?$", re.IGNORECASE
)


def _clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_case_info(label: str) -> dict[str, str | None]:
    cleaned = _clean_text(label)
    match = re.search(r"(?P<court>[^()\n]+?)\s*\((?P<case_number>\d{1,6}/\d{2,5})\)", cleaned)
    if match:
        return {
            "court": match.group("court").strip(" -"),
            "case_number": match.group("case_number").strip(),
            "label": cleaned,
        }
    return {
        "court": cleaned.split("-")[0].strip() if "-" in cleaned else cleaned,
        "case_number": None,
        "label": cleaned,
    }


def extract_case_links(html: str, base_url: str = BASE_URL) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[dict[str, Any]] = []
    seen: set[str] = set()
    for anchor in soup.select("a[href]"):
        href = (anchor.get("href") or "").strip()
        label = _clean_text(anchor.get_text(" ", strip=True))
        if not href or not label:
            continue
        full_url = urljoin(base_url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        if "/documents/" not in href and not href.lower().endswith(".pdf") and "/uploads/" not in href:
            continue
        details = parse_case_info(label)
        links.append({
            "label": label,
            "url": full_url,
            "court": details["court"],
            "case_number": details["case_number"],
        })
    return links


def _is_likely_document_label(label: str) -> bool:
    lowered = label.lower()
    generic_tokens = [
        "summary all cases",
        "index of documents uploaded on website",
        "website control sheet",
        "daily court dates",
        "court dates",
        "important judgements",
        "library",
        "home trade",
        "quick menu",
        "contact",
    ]
    if any(token in lowered for token in generic_tokens):
        return False
    return True


def parse_longtail_document_page(html: str, base_url: str = BASE_URL) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    title = _clean_text(h1.get_text()) if h1 else (_clean_text(soup.title.get_text()) if soup.title else "Case")
    info = parse_case_info(title)

    document_files = []
    folder_links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        txt = _clean_text(a.get_text(" ", strip=True))
        if "/get-folder-documents/" in href:
            folder_links.append({"label": txt, "url": urljoin(base_url, href)})
        elif ".pdf" in href.lower() or "/uploads/" in href:
            if _is_likely_document_label(txt):
                document_files.append({"label": txt, "title": txt, "url": urljoin(base_url, href)})

    return {
        "case_label": info["label"],
        "court": info["court"],
        "case_number": info["case_number"],
        "document_files": document_files,
        "folder_links": folder_links,
    }


def fetch_soup(url: str, timeout: int = 25) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except Exception as exc:
        print(f"[Scraper] Failed to fetch {url}: {exc}")
    return None


def extract_pdfs_from_soup(soup: BeautifulSoup, base_url: str = BASE_URL) -> list[dict[str, str]]:
    pdfs: list[dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.select("a[href], iframe[src], embed[src], object[data]"):
        href = a.get("href") or a.get("src") or a.get("data")
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
        full_url = urljoin(base_url, href)
        lowered = full_url.lower()

        if ".pdf" in lowered or "/uploads/" in lowered or "/files/" in lowered:
            if full_url not in seen:
                seen.add(full_url)
                label = _clean_text(a.get_text(" ", strip=True))
                if not label:
                    label = Path(unquote(urlparse(full_url).path)).stem or "Document PDF"
                pdfs.append({"title": label, "url": full_url})
    return pdfs


def crawl_subfolder_recursive(
    subfolder_url: str,
    level: int = 2,
    max_depth: int = 5,
    seen_urls: set[str] | None = None,
) -> dict[str, Any]:
    if seen_urls is None:
        seen_urls = set()

    subfolder_id = subfolder_url.rstrip("/").split("/")[-1]
    result: dict[str, Any] = {
        "id": f"sub_{subfolder_id}",
        "url": subfolder_url,
        "title": f"Subfolder {subfolder_id}",
        "level": level,
        "documents": [],
        "subfolders": [],
    }

    if subfolder_url in seen_urls or level > max_depth:
        return result
    seen_urls.add(subfolder_url)

    soup = fetch_soup(subfolder_url)
    if not soup:
        return result

    # Find heading/title
    for h in soup.select("h1, h2, h3, h4, h5, .title"):
        txt = _clean_text(h.get_text(" ", strip=True))
        if txt and "housefull" not in txt.lower() and "contact" not in txt.lower():
            result["title"] = txt
            break

    # Extract PDFs in this subfolder
    result["documents"] = extract_pdfs_from_soup(soup, base_url=subfolder_url)

    # Find nested subfolders
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "/get-sub-folder-documents/" in href:
            full_child_url = urljoin(BASE_URL, href)
            if full_child_url not in seen_urls:
                child_title = _clean_text(a.get_text(" ", strip=True)) or "Child Subfolder"
                child_node = crawl_subfolder_recursive(
                    full_child_url,
                    level=level + 1,
                    max_depth=max_depth,
                    seen_urls=seen_urls,
                )
                child_node["title"] = child_title
                result["subfolders"].append(child_node)

    return result


def crawl_folder_recursive(folder_url: str, seen_urls: set[str] | None = None) -> dict[str, Any]:
    if seen_urls is None:
        seen_urls = set()

    folder_id = folder_url.rstrip("/").split("/")[-1]
    result: dict[str, Any] = {
        "id": f"folder_{folder_id}",
        "url": folder_url,
        "title": f"Folder {folder_id}",
        "level": 1,
        "documents": [],
        "subfolders": [],
    }

    if folder_url in seen_urls:
        return result
    seen_urls.add(folder_url)

    soup = fetch_soup(folder_url)
    if not soup:
        return result

    for h in soup.select("h1, h2, h3, h4, .title"):
        txt = _clean_text(h.get_text(" ", strip=True))
        if txt and "housefull" not in txt.lower() and "contact" not in txt.lower():
            result["title"] = txt
            break

    result["documents"] = extract_pdfs_from_soup(soup, base_url=folder_url)

    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "/get-sub-folder-documents/" in href:
            sub_url = urljoin(BASE_URL, href)
            sub_title = _clean_text(a.get_text(" ", strip=True)) or "Subfolder"
            sub_node = crawl_subfolder_recursive(sub_url, level=2, seen_urls=seen_urls)
            sub_node["title"] = sub_title
            result["subfolders"].append(sub_node)

    return result


def crawl_case_document_page(doc_id: str, case_label: str = "", category: str = "") -> dict[str, Any]:
    url = f"{BASE_URL}/documents/{doc_id}" if not doc_id.startswith("http") else doc_id
    raw_id = doc_id.rstrip("/").split("/")[-1]

    info = parse_case_info(case_label)
    record: dict[str, Any] = {
        "id": raw_id,
        "case_id": f"lt-{raw_id}",
        "case_number": info["case_number"] or f"LT/{raw_id}",
        "court": info["court"] or "General Court",
        "title": case_label or f"Case Record {raw_id}",
        "category": category,
        "url": url,
        "documents": [],
        "folders": [],
    }

    soup = fetch_soup(url)
    if not soup:
        return record

    if not case_label:
        h1 = soup.find("h1")
        if h1 and _clean_text(h1.get_text()):
            record["title"] = _clean_text(h1.get_text())

    # Direct PDFs on document page
    record["documents"] = extract_pdfs_from_soup(soup, base_url=url)

    # Discover folders
    seen_folder_urls = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "/get-folder-documents/" in href:
            f_url = urljoin(BASE_URL, href)
            if f_url not in seen_folder_urls:
                seen_folder_urls.add(f_url)
                f_title = _clean_text(a.get_text(" ", strip=True)) or "Folder"
                folder_node = crawl_folder_recursive(f_url)
                folder_node["title"] = f_title
                record["folders"].append(folder_node)

    return record


def get_homepage_categories_and_cases() -> list[dict[str, Any]]:
    soup = fetch_soup(BASE_URL)
    if not soup:
        return []

    sections: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for h2 in soup.find_all("h2"):
        cat_name = _clean_text(h2.get_text(" ", strip=True))
        if not cat_name or "quick menu" in cat_name.lower() or "contact" in cat_name.lower():
            continue

        parent = h2.find_parent("section") or h2.find_parent("div", class_="container") or h2.parent
        if not parent:
            continue

        for a in parent.find_all("a", href=True):
            href = a.get("href", "")
            if not href or href in ["#", "/"] or "contact" in href.lower():
                continue

            full_url = urljoin(BASE_URL, href)
            if full_url in seen_urls:
                continue

            is_doc = "/documents/" in full_url
            is_pdf = ".pdf" in full_url.lower() or "/uploads/" in full_url

            if is_doc or is_pdf:
                seen_urls.add(full_url)
                txt = _clean_text(a.get_text(" ", strip=True))
                doc_id = full_url.rstrip("/").split("/")[-1]
                sections.append({
                    "category": cat_name,
                    "title": txt or f"Record {doc_id}",
                    "url": full_url,
                    "doc_id": doc_id,
                    "is_pdf": is_pdf,
                })

    return sections


def harvest_all_longtail_hierarchy(limit_cases: int | None = None) -> dict[str, Any]:
    """
    Crawls the entire longtail hierarchy:
    Categories -> Cases -> Folders -> Subfolders -> PDF Documents.
    Saves JSON snapshot to `data/longtail_catalog_tree.json`.
    """
    print("[Harvest] Starting complete longtailcases.com hierarchy crawl...")
    items = get_homepage_categories_and_cases()
    if not items:
        if _CATALOG_CACHE:
            return _CATALOG_CACHE
        return {"categories": {}, "total_cases": 0, "total_documents": 0}

    catalog: dict[str, list[dict[str, Any]]] = {}
    total_docs = 0
    cases_crawled = 0

    for item in items:
        cat = item["category"]
        if cat not in catalog:
            catalog[cat] = []

        if item["is_pdf"]:
            # Direct PDF category item (e.g. MIS.pdf, DAILY COURT DATES.pdf)
            catalog[cat].append({
                "id": item["doc_id"],
                "case_id": f"mis-{item['doc_id']}",
                "title": item["title"],
                "category": cat,
                "url": item["url"],
                "case_number": "MIS/SUMMARY",
                "court": "Registry / MIS",
                "documents": [{"title": item["title"], "url": item["url"]}],
                "folders": [],
            })
            total_docs += 1
        else:
            doc_id = item["doc_id"]
            case_data = crawl_case_document_page(doc_id, case_label=item["title"], category=cat)
            catalog[cat].append(case_data)
            
            # Count PDFs
            doc_count = len(case_data.get("documents", []))
            for f in case_data.get("folders", []):
                doc_count += len(f.get("documents", []))
                for sf in f.get("subfolders", []):
                    doc_count += len(sf.get("documents", []))
            total_docs += doc_count
            cases_crawled += 1

        if limit_cases is not None and cases_crawled >= limit_cases:
            break

    result = {
        "source": BASE_URL,
        "total_categories": len(catalog),
        "total_cases": sum(len(v) for v in catalog.values()),
        "total_documents": total_docs,
        "categories": catalog,
    }

    # Cache in memory
    _CATALOG_CACHE.clear()
    _CATALOG_CACHE.update(result)

    print(f"[Harvest] Completed. Captured {result['total_cases']} cases across {len(catalog)} categories.")
    return result


def get_cached_or_live_catalog() -> dict[str, Any]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE:
        return enrich_catalog_with_doc_details(_CATALOG_CACHE)
    cat = harvest_all_longtail_hierarchy(limit_cases=12)
    return enrich_catalog_with_doc_details(cat)


def enrich_catalog_with_doc_details(catalog: dict[str, Any]) -> dict[str, Any]:
    categories = catalog.get("categories", {})
    try:
        from app.db.session import SessionLocal
        from app.db.models import Document
        db = SessionLocal()
        existing_doc_ids = {
            r[0] for r in db.query(Document.id).filter(Document.extracted_text.isnot(None), Document.extracted_text != "").all()
        }
        db.close()
    except Exception:
        existing_doc_ids = set()

    for cat_name, cases in categories.items():
        for case in cases:
            # Process direct docs
            for doc in case.get("documents", []):
                url = doc.get("url") or ""
                doc_slug = re.sub(r"[^a-zA-Z0-9]", "_", url.split("/")[-1])[:32]
                doc_id = f"doc-{doc_slug}"
                doc["doc_id"] = doc_id
                doc["has_txt"] = doc_id in existing_doc_ids

            # Process folder docs
            for folder in case.get("folders", []):
                for fdoc in folder.get("documents", []):
                    url = fdoc.get("url") or ""
                    doc_slug = re.sub(r"[^a-zA-Z0-9]", "_", url.split("/")[-1])[:32]
                    doc_id = f"doc-{doc_slug}"
                    fdoc["doc_id"] = doc_id
                    fdoc["has_txt"] = doc_id in existing_doc_ids

                for sub in folder.get("subfolders", []):
                    for sdoc in sub.get("documents", []):
                        url = sdoc.get("url") or ""
                        doc_slug = re.sub(r"[^a-zA-Z0-9]", "_", url.split("/")[-1])[:32]
                        doc_id = f"doc-{doc_slug}"
                        sdoc["doc_id"] = doc_id
                        sdoc["has_txt"] = doc_id in existing_doc_ids

    return catalog


def sync_catalog_to_database(catalog: dict[str, Any]) -> int:
    """Syncs the hierarchical catalog into SQLite/PostgreSQL relational tables."""
    db = SessionLocal()
    count = 0
    try:
        categories = catalog.get("categories", {})
        for cat_name, cases in categories.items():
            for case_dict in cases:
                case_id = str(case_dict.get("case_id") or f"lt-{case_dict.get('id')}")
                title = case_dict.get("title") or "Untitled Case"
                court = case_dict.get("court") or "District Court"
                case_num = case_dict.get("case_number") or f"CASE/{case_id}"

                # Ensure Court exists
                court_id = f"court-{re.sub(r'[^a-zA-Z0-9]', '_', court.lower())[:32]}"
                existing_court = db.query(Court).filter_by(id=court_id).first()
                if not existing_court:
                    new_court = Court(
                        id=court_id,
                        name=court,
                        jurisdiction=cat_name,
                        state=cat_name if cat_name in ["Maharashtra", "Gujarat", "Delhi", "Kolkata"] else "National",
                    )
                    db.add(new_court)
                    db.commit()

                # Case
                existing_case = db.query(Case).filter_by(id=case_id).first()
                if not existing_case:
                    new_case = Case(
                        id=case_id,
                        case_number=case_num,
                        case_type="Criminal / Civil Record",
                        title=title,
                        court_name=court,
                        court_id=court_id,
                        subject=cat_name,
                        source_url=case_dict.get("url"),
                        canonical_url=f"/cases/{case_id}",
                        summary=f"Hierarchical case record for {title} under {cat_name}.",
                    )
                    db.add(new_case)
                    db.commit()

                # Process root documents
                for doc in case_dict.get("documents", []):
                    doc_url = doc.get("url")
                    doc_id = f"doc-{re.sub(r'[^a-zA-Z0-9]', '_', doc_url.split('/')[-1])[:32]}"
                    if not db.query(Document).filter_by(id=doc_id).first():
                        new_doc = Document(
                            id=doc_id,
                            case_id=case_id,
                            title=doc.get("title") or "Document PDF",
                            source_url=case_dict.get("url"),
                            original_pdf_url=doc_url,
                            document_type="Document",
                            court=court,
                        )
                        db.add(new_doc)
                        count += 1

                # Process folders and subfolders
                for folder in case_dict.get("folders", []):
                    folder_id = str(folder.get("id") or f"f_{case_id}_{re.sub(r'[^a-zA-Z0-9]', '_', folder.get('title', ''))[:20]}")
                    if not db.query(LongtailFolder).filter_by(id=folder_id).first():
                        db_folder = LongtailFolder(
                            id=folder_id,
                            case_id=case_id,
                            title=folder.get("title") or "Folder",
                            source_url=folder.get("url"),
                            folder_type="folder",
                            level=1,
                        )
                        db.add(db_folder)
                        db.commit()

                    for f_doc in folder.get("documents", []):
                        f_doc_url = f_doc.get("url")
                        f_doc_id = f"doc-{re.sub(r'[^a-zA-Z0-9]', '_', f_doc_url.split('/')[-1])[:32]}"
                        if not db.query(Document).filter_by(id=f_doc_id).first():
                            new_doc = Document(
                                id=f_doc_id,
                                case_id=case_id,
                                folder_id=folder_id,
                                title=f_doc.get("title") or "Folder Document PDF",
                                source_url=folder.get("url"),
                                original_pdf_url=f_doc_url,
                                document_type="Application / Order",
                                court=court,
                            )
                            db.add(new_doc)
                            count += 1

                    for sub in folder.get("subfolders", []):
                        sub_id = str(sub.get("id") or f"sf_{folder_id}_{re.sub(r'[^a-zA-Z0-9]', '_', sub.get('title', ''))[:20]}")
                        if not db.query(LongtailFolder).filter_by(id=sub_id).first():
                            db_sub = LongtailFolder(
                                id=sub_id,
                                case_id=case_id,
                                parent_id=folder_id,
                                title=sub.get("title") or "Subfolder",
                                source_url=sub.get("url"),
                                folder_type="subfolder",
                                level=2,
                            )
                            db.add(db_sub)
                            db.commit()

                        for sf_doc in sub.get("documents", []):
                            sf_doc_url = sf_doc.get("url")
                            sf_doc_id = f"doc-{re.sub(r'[^a-zA-Z0-9]', '_', sf_doc_url.split('/')[-1])[:32]}"
                            if not db.query(Document).filter_by(id=sf_doc_id).first():
                                new_doc = Document(
                                    id=sf_doc_id,
                                    case_id=case_id,
                                    folder_id=sub_id,
                                    title=sf_doc.get("title") or "Subfolder Document PDF",
                                    source_url=sub.get("url"),
                                    original_pdf_url=sf_doc_url,
                                    document_type="Document",
                                    court=court,
                                )
                                db.add(new_doc)
                                count += 1
                db.commit()
    finally:
        db.close()
    return count
