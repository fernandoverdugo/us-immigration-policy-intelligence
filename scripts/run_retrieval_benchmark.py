from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NLP_DIR = Path("analysis/nlp/results")
OUTPUT_DIR = Path("analysis/retrieval/results")
BENCHMARK_PATH = Path("analysis/retrieval/benchmark_queries.csv")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_policy_documents() -> pd.DataFrame:
    assignments = pd.read_csv(NLP_DIR / "cluster_assignments.csv")
    text = pd.read_csv(NLP_DIR / "document_text.csv")

    merged = assignments.merge(
        text[
            [
                "document_number",
                "text",
            ]
        ],
        on="document_number",
        how="left",
        validate="one_to_one",
    )
    return merged


def build_tfidf_index(
    documents: pd.DataFrame,
) -> tuple[TfidfVectorizer, object]:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=1,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(documents["text"].fillna(""))
    return vectorizer, matrix


def embed_documents(
    model: SentenceTransformer,
    documents: pd.DataFrame,
) -> np.ndarray:
    return model.encode(
        documents["text"].fillna("").tolist(),
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    return np.argsort(scores)[::-1][:k]


def evaluate_query(
    documents: pd.DataFrame,
    query: str,
    target_cluster: int,
    tfidf_vectorizer: TfidfVectorizer,
    tfidf_matrix,
    embedding_model: SentenceTransformer,
    embedding_matrix: np.ndarray,
    k: int = 5,
) -> tuple[dict, list[dict]]:
    tfidf_query = tfidf_vectorizer.transform([query])
    tfidf_scores = cosine_similarity(tfidf_query, tfidf_matrix).ravel()

    semantic_query = embedding_model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    semantic_scores = embedding_matrix @ semantic_query

    rows = []
    summary = {}

    for method, scores in [
        ("tfidf", tfidf_scores),
        ("semantic", semantic_scores),
    ]:
        indices = top_k_indices(scores, k)
        retrieved = documents.iloc[indices].copy()
        hits = retrieved["cluster"].eq(target_cluster).astype(int)

        summary[f"{method}_precision_at_{k}"] = float(hits.mean())
        summary[f"{method}_hit_at_{k}"] = int(hits.sum() > 0)
        first_hit = np.flatnonzero(hits.to_numpy())
        summary[f"{method}_reciprocal_rank_at_{k}"] = (
            float(1 / (first_hit[0] + 1)) if len(first_hit) else 0.0
        )

        for rank, (idx, row) in enumerate(retrieved.iterrows(), start=1):
            rows.append(
                {
                    "method": method,
                    "query": query,
                    "target_cluster": target_cluster,
                    "rank": rank,
                    "document_number": row["document_number"],
                    "retrieved_cluster": int(row["cluster"]),
                    "score": float(scores[idx]),
                    "title": row["title"],
                    "is_target_cluster": int(row["cluster"] == target_cluster),
                }
            )

    return summary, rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = load_policy_documents()
    benchmark = pd.read_csv(BENCHMARK_PATH)

    tfidf_vectorizer, tfidf_matrix = build_tfidf_index(documents)
    model = SentenceTransformer(MODEL_NAME)
    embedding_matrix = embed_documents(model, documents)

    retrieval_rows = []
    benchmark_rows = []

    for _, item in benchmark.iterrows():
        metrics, rows = evaluate_query(
            documents=documents,
            query=item["query"],
            target_cluster=int(item["target_cluster"]),
            tfidf_vectorizer=tfidf_vectorizer,
            tfidf_matrix=tfidf_matrix,
            embedding_model=model,
            embedding_matrix=embedding_matrix,
        )

        benchmark_rows.append(
            {
                "query_id": item["query_id"],
                "query": item["query"],
                "target_cluster": int(item["target_cluster"]),
                **metrics,
            }
        )
        retrieval_rows.extend(rows)

    benchmark_results = pd.DataFrame(benchmark_rows)
    retrieval_results = pd.DataFrame(retrieval_rows)

    aggregate = {
        "queries": int(len(benchmark_results)),
        "documents": int(len(documents)),
        "embedding_model": MODEL_NAME,
        "evaluation_note": (
            "Target clusters are analyst-interpreted exploratory policy topics, "
            "not legal relevance judgments."
        ),
    }

    for method in ["tfidf", "semantic"]:
        aggregate[f"{method}_mean_precision_at_5"] = float(
            benchmark_results[f"{method}_precision_at_5"].mean()
        )
        aggregate[f"{method}_hit_rate_at_5"] = float(
            benchmark_results[f"{method}_hit_at_5"].mean()
        )
        aggregate[f"{method}_mean_reciprocal_rank_at_5"] = float(
            benchmark_results[f"{method}_reciprocal_rank_at_5"].mean()
        )

    np.save(OUTPUT_DIR / "semantic_embeddings.npy", embedding_matrix)
    documents[
        [
            "document_number",
            "publication_date",
            "document_type",
            "title",
            "agency_scopes",
            "cluster",
        ]
    ].to_csv(OUTPUT_DIR / "embedding_index.csv", index=False)
    benchmark_results.to_csv(OUTPUT_DIR / "benchmark_results.csv", index=False)
    retrieval_results.to_csv(OUTPUT_DIR / "retrieval_examples.csv", index=False)
    (OUTPUT_DIR / "retrieval_summary.json").write_text(
        json.dumps(aggregate, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()
