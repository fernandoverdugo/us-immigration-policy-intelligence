from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.retrieval.embedding import MODEL_NAME, create_embedding_model

RESULTS_DIR = Path("analysis/retrieval/results")
CLUSTER_LABELS_PATH = Path("analysis/nlp/cluster_labels.csv")


@lru_cache(maxsize=1)
def load_index() -> tuple[pd.DataFrame, np.ndarray]:
    metadata = pd.read_csv(RESULTS_DIR / "embedding_index.csv")
    embeddings = np.load(RESULTS_DIR / "semantic_embeddings.npy")

    if len(metadata) != len(embeddings):
        raise ValueError("Embedding index metadata and vectors are misaligned.")

    return metadata, embeddings


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


def semantic_search(query: str, k: int = 10) -> list[dict]:
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
    indices = np.argsort(scores)[::-1][:k]

    results = []
    for rank, idx in enumerate(indices, start=1):
        row = metadata.iloc[idx]
        results.append(
            {
                "rank": rank,
                "document_number": row["document_number"],
                "publication_date": row["publication_date"],
                "document_type": row["document_type"],
                "title": row["title"],
                "agency_scopes": row["agency_scopes"],
                "cluster": int(row["cluster"]),
                "topic": labels.get(int(row["cluster"]), "Unlabeled policy topic"),
                "source_url": (
                    "https://www.federalregister.gov/d/"
                    + str(row["document_number"])
                ),
                "score": float(scores[idx]),
            }
        )

    return results
