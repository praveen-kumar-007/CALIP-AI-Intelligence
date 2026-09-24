import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "CALIP" in response.text
    assert "AI-Readable Legal" in response.text


def test_cases_page_loads():
    response = client.get("/cases")
    assert response.status_code == 200
    assert "Legal Cases Repository" in response.text


def test_longtail_hierarchy_page_loads():
    response = client.get("/longtail")
    assert response.status_code == 200
    assert "Longtail Cases Hierarchical Catalog" in response.text


def test_robots_txt():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "User-agent: *" in response.text
    assert "Disallow: /admin/" in response.text
    assert "Sitemap: https://longtailcases.com/sitemap.xml" in response.text


def test_sitemap_xml():
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "sitemapindex" in response.text


def test_api_cases():
    response = client.get("/api/cases?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0


def test_api_search():
    response = client.get("/api/search?q=Nagpur")
    assert response.status_code == 200
    data = response.json()
    assert "cases_matched" in data


def test_api_rag_ask():
    response = client.get("/api/rag/ask?query=What+cases+are+recorded?")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


def test_llms_txt():
    response = client.get("/llms.txt")
    assert response.status_code == 200
    assert "CALIP" in response.text
    assert "Fast Links for LLMs & Crawlers" in response.text
    assert "/api/open/dump" in response.text
    assert "No API keys" in response.text


def test_llms_full_txt():
    response = client.get("/llms-full.txt")
    assert response.status_code == 200
    assert "CALIP PLATFORM COMPLETE KNOWLEDGE CORPUS" in response.text
    assert "LEGAL CASES REPOSITORY" in response.text


def test_api_open_dump():
    response = client.get("/api/open/dump")
    assert response.status_code == 200
    data = response.json()
    assert data["access"] == "open_unrestricted"
    assert "cases" in data
    assert "documents" in data
    assert "statistics" in data


def test_api_open_cases():
    response = client.get("/api/open/cases")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data
    assert len(data["items"]) > 0


def test_api_open_documents():
    response = client.get("/api/open/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data


def test_api_open_ask():
    response = client.get("/api/open/ask?query=Nagpur+case")
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


def test_api_open_schema():
    response = client.get("/api/open/schema")
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "endpoints" in data


def test_robots_ai_bots():
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "ClaudeBot" in response.text
    assert "Claude-Web" in response.text
    assert "GPTBot" in response.text
    assert "PerplexityBot" in response.text
    assert "Allow: /api/open/" in response.text
    assert "Disallow: /admin/" in response.text


def test_cors_headers():
    response = client.get("/api/open/dump", headers={"Origin": "https://claude.ai"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ["*", "https://claude.ai"]


def test_settings_configuration():
    from app.core.config import settings
    assert settings.APP_NAME
    assert settings.DATA_DIR.exists()
    assert settings.DOWNLOADS_DIR.exists()
    assert settings.INCOMING_DIR.exists()
    assert settings.OCR_STORAGE_DIR.exists()
    assert settings.DATABASE_URL
    assert "longtailcases.com" in settings.LONGTAIL_BASE_URL

