from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.retrieval.search import (
    MODEL_NAME,
    load_cluster_labels,
    load_index,
    semantic_search,
)

WEB_DIR = Path("web")

app = FastAPI(
    title="U.S. Immigration Policy Intelligence API",
    version="0.2.0",
    description=(
        "Search and explore the project's Federal Register immigration-policy corpus."
    ),
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    metadata, _ = load_index()
    return {
        "status": "ok",
        "documents": len(metadata),
        "retrieval_model": MODEL_NAME,
    }


@app.get("/topics")
def topics() -> dict:
    labels = load_cluster_labels()
    return {
        "count": len(labels),
        "topics": [
            {"cluster": cluster, "label": label}
            for cluster, label in sorted(labels.items())
        ],
    }


@app.get("/search")
def search(
    q: str = Query(min_length=2, max_length=500),
    k: int = Query(default=10, ge=1, le=50),
) -> dict:
    try:
        results = semantic_search(q, k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


@app.get("/documents/{document_number}")
def document(document_number: str) -> dict:
    metadata, _ = load_index()
    labels = load_cluster_labels()
    matches = metadata.loc[
        metadata["document_number"].astype(str) == document_number
    ]

    if matches.empty:
        raise HTTPException(status_code=404, detail="Document not found.")

    row = matches.iloc[0]
    cluster = int(row["cluster"])

    return {
        "document_number": row["document_number"],
        "publication_date": row["publication_date"],
        "document_type": row["document_type"],
        "title": row["title"],
        "agency_scopes": row["agency_scopes"],
        "cluster": cluster,
        "topic": labels.get(cluster, "Unlabeled policy topic"),
        "source_url": f"https://www.federalregister.gov/d/{document_number}",
    }
