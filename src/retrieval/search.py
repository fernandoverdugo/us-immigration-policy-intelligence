from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

RESULTS_DIR = Path("analysis/retrieval/results")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_index() -> tuple[pd.DataFrame, np.ndarray]:
    metadata = pd.read_csv(RESULTS_DIR / "embedding_index.csv")
    embeddings = np.load(RESULTS_DIR / "semantic_embeddings.npy")

    if len(metadata) != len(embeddings):
        raise ValueError("Embedding index metadata and vectors are misaligned.")

    return metadata, embeddings


@lru_cache(maxsize=1)
def load_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def semantic_search(query: str, k: int = 10) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")
    if k < 1 or k > 50:
        raise ValueError("k must be between 1 and 50.")

    metadata, embeddings = load_index()
    model = load_model()

    query_vector = model.encode(
        [query.strip()],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

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
                "score": float(scores[idx]),
            }
        )

    return results
