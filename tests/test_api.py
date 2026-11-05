from fastapi.testclient import TestClient
import pandas as pd

import api.main as api_main


client = TestClient(api_main.app)


def test_home_serves_web_interface():
    response = client.get("/")
    assert response.status_code == 200
    assert "U.S. Immigration Policy Intelligence" in response.text


def test_document_page_serves_interface():
    response = client.get("/document/TEST-1")
    assert response.status_code == 200
    assert "Federal Register document" in response.text


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["documents"] > 0
    assert "deployment_commit" in payload


def test_about_endpoint():
    response = client.get("/about")
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"] > 0
    assert payload["topics"] > 0
    assert 0 <= payload["semantic_precision_at_5"] <= 1
    assert payload["start_year"] <= payload["end_year"]


def test_topics_endpoint():
    response = client.get("/topics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 9
    assert len(payload["topics"]) == 9


def test_document_not_found():
    response = client.get("/documents/NOT-A-DOCUMENT")
    assert response.status_code == 404


def test_search_endpoint_forwards_filters(monkeypatch):
    captured = {}

    def fake_search(query, k, **kwargs):
        captured.update(kwargs)
        return [
            {
                "rank": 1,
                "document_number": "TEST-1",
                "publication_date": "2026-01-01",
                "document_type": "Rule",
                "title": "Test Result",
                "agency_scopes": "uscis",
                "cluster": 1,
                "topic": "Asylum and removal rulemaking",
                "snippet": "A concise abstract snippet.",
                "detail_url": "/document/TEST-1",
                "source_url": "https://www.federalregister.gov/d/TEST-1",
                "score": 0.9,
            }
        ]

    monkeypatch.setattr(api_main, "semantic_search", fake_search)

    response = client.get(
        "/search",
        params={
            "q": "asylum rules",
            "k": 1,
            "year": 2026,
            "agency": "uscis",
            "document_type": "Rule",
            "topic": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["snippet"] == "A concise abstract snippet."
    assert captured == {
        "year": 2026,
        "agency": "uscis",
        "document_type": "Rule",
        "topic": 1,
    }


def test_rich_document_endpoint(monkeypatch):
    frame = pd.DataFrame(
        [
            {
                "document_number": "TEST-1",
                "publication_date": "2026-01-01",
                "document_type": "Rule",
                "title": "Test Rule",
                "abstract": "Detailed abstract.",
                "action": "Final rule.",
                "effective_on": "2026-02-01",
                "comments_close_on": None,
                "citation": "91 FR 1234",
                "agency_scopes": "uscis",
                "cfr_references": "8 CFR 208 | 8 CFR 274a",
                "regulation_identifiers": "1615-ABCD",
                "html_url": "https://www.federalregister.gov/d/TEST-1",
                "pdf_url": "https://example.com/test.pdf",
                "raw_text_url": None,
                "cluster": 1,
            }
        ]
    )

    monkeypatch.setattr(api_main, "load_index", lambda: (frame, None))
    monkeypatch.setattr(
        api_main,
        "load_cluster_labels",
        lambda: {1: "Asylum and removal rulemaking"},
    )
    monkeypatch.setattr(api_main, "related_documents", lambda _: [])

    response = client.get("/documents/TEST-1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["abstract"] == "Detailed abstract."
    assert payload["cfr_references"] == ["8 CFR 208", "8 CFR 274a"]
    assert payload["regulation_identifiers"] == ["1615-ABCD"]
    assert payload["effective_on"] == "2026-02-01"
