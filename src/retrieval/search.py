from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.retrieval.embedding import MODEL_NAME, create_embedding_model

RESULTS_DIR = Path("analysis/retrieval/results")
NLP_RESULTS_DIR = Path("analysis/nlp/results")
CLUSTER_LABELS_PATH = Path("analysis/nlp/cluster_labels.csv")


def clean_value(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


@lru_cache(maxsize=1)
def load_index() -> tuple[pd.DataFrame, np.ndarray]:
    metadata = pd.read_csv(RESULTS_DIR / "embedding_index.csv")
    embeddings = np.load(RESULTS_DIR / "semantic_embeddings.npy")

    if len(metadata) != len(embeddings):
        raise ValueError("Embedding index metadata and vectors are misaligned.")

    app_metadata = pd.read_csv(NLP_RESULTS_DIR / "document_metadata.csv")
    app_metadata = app_metadata.loc[
        app_metadata["nlp_scope"].eq("substantive_policy")
    ].copy()

    merged = metadata.merge(
        app_metadata,
        on=[
            "document_number",
            "publication_date",
            "document_type",
            "title",
            "agency_scopes",
        ],
        how="left",
        validate="one_to_one",
    )

    return merged, embeddings


@lru_cache(maxsize=1)
def load_cluster_labels() -> dict[int, str]:
    frame = pd.read_csv(CLUSTER_LABELS_PATH)
    return {
        int(row["cluster"]): str(row["analyst_label"])
        for _, row in frame.iterrows()
    }


@lru_cache(maxsize=1)
def load_model() -> Any:
    return create_embedding_model()


def make_snippet(abstract: Any, limit: int = 280) -> str | None:
    text = clean_value(abstract)
    if not text:
        return None
    if len(text) <= limit:
        return text
    shortened = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return shortened + "…"


def filter_mask(
    metadata: pd.DataFrame,
    *,
    year: int | None = None,
    agency: str | None = None,
    document_type: str | None = None,
    topic: int | None = None,
) -> np.ndarray:
    mask = np.ones(len(metadata), dtype=bool)

    if year is not None:
        years = pd.to_datetime(
            metadata["publication_date"],
            errors="coerce",
        ).dt.year
        mask &= years.eq(year).to_numpy()

    if agency:
        agency_value = agency.strip().lower()
        mask &= (
            metadata["agency_scopes"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.split(" | ", regex=False)
            .apply(lambda values: agency_value in values)
            .to_numpy()
        )

    if document_type:
        mask &= (
            metadata["document_type"]
            .fillna("")
            .astype(str)
            .str.casefold()
            .eq(document_type.strip().casefold())
            .to_numpy()
        )

    if topic is not None:
        mask &= metadata["cluster"].astype(int).eq(topic).to_numpy()

    return mask


def search_filter_options() -> dict:
    metadata, _ = load_index()
    labels = load_cluster_labels()

    years = sorted(
        {
            int(year)
            for year in pd.to_datetime(
                metadata["publication_date"],
                errors="coerce",
            ).dt.year.dropna()
        },
        reverse=True,
    )

    agencies = sorted(
        {
            agency
            for scopes in metadata["agency_scopes"].fillna("").astype(str)
            for agency in scopes.split(" | ")
            if agency
        }
    )

    document_types = sorted(
        metadata["document_type"].dropna().astype(str).unique().tolist()
    )

    return {
        "years": years,
        "agencies": agencies,
        "document_types": document_types,
        "topics": [
            {"cluster": cluster, "label": label}
            for cluster, label in sorted(labels.items())
        ],
    }


def semantic_search(
    query: str,
    k: int = 10,
    *,
    year: int | None = None,
    agency: str | None = None,
    document_type: str | None = None,
    topic: int | None = None,
) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")
    if k < 1 or k > 50:
        raise ValueError("k must be between 1 and 50.")

    metadata, embeddings = load_index()
    labels = load_cluster_labels()
    model = load_model()

    query_vector = np.asarray(
        list(model.query_embed(query.strip()))[0],
        dtype=np.float32,
    )
    norm = np.linalg.norm(query_vector)
    if norm:
        query_vector = query_vector / norm

    scores = embeddings @ query_vector
    mask = filter_mask(
        metadata,
        year=year,
        agency=agency,
        document_type=document_type,
        topic=topic,
    )
    candidate_indices = np.flatnonzero(mask)

    if not len(candidate_indices):
        return []

    ranked_candidates = candidate_indices[
        np.argsort(scores[candidate_indices])[::-1]
    ][:k]

    results = []
    for rank, idx in enumerate(ranked_candidates, start=1):
        row = metadata.iloc[idx]
        document_number = str(row["document_number"])
        cluster = int(row["cluster"])
        results.append(
            {
                "rank": rank,
                "document_number": document_number,
                "publication_date": row["publication_date"],
                "document_type": row["document_type"],
                "title": row["title"],
                "agency_scopes": row["agency_scopes"],
                "cluster": cluster,
                "topic": labels.get(cluster, "Unlabeled policy topic"),
                "snippet": make_snippet(row.get("abstract")),
                "detail_url": f"/document/{document_number}",
                "source_url": clean_value(row.get("html_url"))
                or (
                    "https://www.federalregister.gov/d/"
                    + document_number
                ),
                "score": float(scores[idx]),
            }
        )

    return results
