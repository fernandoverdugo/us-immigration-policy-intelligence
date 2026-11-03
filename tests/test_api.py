from fastapi.testclient import TestClient

import api.main as api_main


client = TestClient(api_main.app)


def test_home_serves_web_interface():
    response = client.get("/")
    assert response.status_code == 200
    assert "U.S. Immigration Policy Intelligence" in response.text


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["documents"] > 0
    assert "deployment_commit" in payload


def test_topics_endpoint():
    response = client.get("/topics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 9
    assert len(payload["topics"]) == 9


def test_document_not_found():
    response = client.get("/documents/NOT-A-DOCUMENT")
    assert response.status_code == 404


def test_search_endpoint_uses_retrieval_service(monkeypatch):
    def fake_search(query, k):
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
                "source_url": "https://www.federalregister.gov/d/TEST-1",
                "score": 0.9,
            }
        ]

    monkeypatch.setattr(api_main, "semantic_search", fake_search)

    response = client.get("/search", params={"q": "asylum rules", "k": 1})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["results"][0]["document_number"] == "TEST-1"
