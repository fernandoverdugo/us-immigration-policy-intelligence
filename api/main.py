from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.retrieval.search import (
    MODEL_NAME,
    clean_value,
    load_cluster_labels,
    load_index,
    search_filter_options,
    semantic_search,
)

WEB_DIR = Path("web")
SIMILARITY_PATH = Path("analysis/nlp/results/document_similarity.csv")

app = FastAPI(
    title="U.S. Immigration Policy Intelligence API",
    version="0.3.0",
    description=(
        "Search and explore the project's Federal Register immigration-policy corpus."
    ),
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/document/{document_number}", include_in_schema=False)
def document_page(document_number: str):
    return FileResponse(WEB_DIR / "document.html")


@app.get("/health")
def health() -> dict:
    metadata, _ = load_index()
    return {
        "status": "ok",
        "documents": len(metadata),
        "retrieval_model": MODEL_NAME,
        "deployment_commit": os.environ.get("RENDER_GIT_COMMIT"),
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


@app.get("/filters")
def filters() -> dict:
    return search_filter_options()


@app.get("/search")
def search(
    q: str = Query(min_length=2, max_length=500),
    k: int = Query(default=10, ge=1, le=50),
    year: int | None = Query(default=None, ge=2017, le=2026),
    agency: str | None = Query(default=None, max_length=50),
    document_type: str | None = Query(default=None, max_length=50),
    topic: int | None = Query(default=None, ge=0),
) -> dict:
    try:
        results = semantic_search(
            q,
            k,
            year=year,
            agency=agency,
            document_type=document_type,
            topic=topic,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "query": q,
        "count": len(results),
        "filters": {
            "year": year,
            "agency": agency,
            "document_type": document_type,
            "topic": topic,
        },
        "results": results,
    }


def split_pipe(value) -> list[str]:
    text = clean_value(value)
    if not text:
        return []
    return [item.strip() for item in text.split(" | ") if item.strip()]


def related_documents(document_number: str) -> list[dict]:
    if not SIMILARITY_PATH.exists():
        return []

    similarity = pd.read_csv(SIMILARITY_PATH)
    rows = similarity.loc[
        similarity["document_number"].astype(str) == document_number
    ].sort_values("rank")

    return [
        {
            "document_number": str(row["related_document_number"]),
            "title": row["related_title"],
            "cosine_similarity": float(row["cosine_similarity"]),
            "detail_url": f"/document/{row['related_document_number']}",
        }
        for _, row in rows.head(3).iterrows()
    ]


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
        "document_number": str(row["document_number"]),
        "publication_date": clean_value(row.get("publication_date")),
        "document_type": clean_value(row.get("document_type")),
        "title": clean_value(row.get("title")),
        "abstract": clean_value(row.get("abstract")),
        "action": clean_value(row.get("action")),
        "effective_on": clean_value(row.get("effective_on")),
        "comments_close_on": clean_value(row.get("comments_close_on")),
        "citation": clean_value(row.get("citation")),
        "agency_scopes": split_pipe(row.get("agency_scopes")),
        "cfr_references": split_pipe(row.get("cfr_references")),
        "regulation_identifiers": split_pipe(row.get("regulation_identifiers")),
        "cluster": cluster,
        "topic": labels.get(cluster, "Unlabeled policy topic"),
        "html_url": clean_value(row.get("html_url"))
        or f"https://www.federalregister.gov/d/{document_number}",
        "pdf_url": clean_value(row.get("pdf_url")),
        "raw_text_url": clean_value(row.get("raw_text_url")),
        "related_documents": related_documents(document_number),
    }
