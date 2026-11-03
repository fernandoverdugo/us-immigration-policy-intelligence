from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

OUTPUT_DIR = Path("analysis/nlp")


def load_documents(database_url: str) -> pd.DataFrame:
    query = """
    SELECT
        d.document_number,
        d.publication_date,
        d.document_type,
        d.title,
        d.abstract,
        d.action,
        d.effective_on,
        d.comments_close_on,
        d.citation,
        d.html_url,
        d.pdf_url,
        d.raw_text_url,
        d.action,
        d.effective_on,
        d.comments_close_on,
        d.citation,
        d.html_url,
        d.pdf_url,
        d.raw_text_url,
        STRING_AGG(
            DISTINCT ce.evidence_value,
            ' | '
            ORDER BY ce.evidence_value
        ) FILTER (WHERE ce.evidence_type = 'source_scope') AS agency_scopes,
        STRING_AGG(
            DISTINCT (cr.title_number::text || ' CFR ' || cr.part),
            ' | '
            ORDER BY (cr.title_number::text || ' CFR ' || cr.part)
        ) AS cfr_references,
        STRING_AGG(
            DISTINCT dri.rin,
            ' | '
            ORDER BY dri.rin
        ) AS regulation_identifiers
    FROM documents d
    LEFT JOIN corpus_evidence ce
        ON ce.document_number = d.document_number
    LEFT JOIN document_cfr_references dcr
        ON dcr.document_number = d.document_number
    LEFT JOIN cfr_references cr
        ON cr.cfr_reference_id = dcr.cfr_reference_id
    LEFT JOIN document_regulation_identifiers dri
        ON dri.document_number = d.document_number
    GROUP BY
        d.document_number,
        d.publication_date,
        d.document_type,
        d.title,
        d.abstract
    ORDER BY d.publication_date, d.document_number
    """

    with psycopg.connect(database_url) as connection:
        return pd.read_sql(query, connection)


def build_text(frame: pd.DataFrame) -> pd.Series:
    titles = frame["title"].fillna("").astype(str).str.strip()
    abstracts = frame["abstract"].fillna("").astype(str).str.strip()
    return (titles + ". " + abstracts).str.split().str.join(" ").str.strip()


def nlp_scope(frame: pd.DataFrame) -> pd.Series:
    text = build_text(frame).str.lower()
    routine_notice = frame["document_type"].eq("Notice") & (
        text.str.contains("information collection", regex=False)
        | text.str.contains("paperwork reduction act", regex=False)
    )
    return pd.Series(
        np.where(
            routine_notice,
            "administrative_information_collection",
            "substantive_policy",
        ),
        index=frame.index,
    )


def fit_tfidf(text: pd.Series) -> tuple[TfidfVectorizer, np.ndarray]:
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=3,
        max_df=0.90,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(text)
    return vectorizer, matrix


def top_terms_by_group(
    frame: pd.DataFrame,
    matrix,
    vectorizer: TfidfVectorizer,
    group_column: str,
    top_n: int = 15,
) -> pd.DataFrame:
    feature_names = np.array(vectorizer.get_feature_names_out())
    rows = []

    for group_value in sorted(frame[group_column].dropna().astype(str).unique()):
        mask = frame[group_column].astype(str).to_numpy() == group_value
        if mask.sum() == 0:
            continue

        mean_scores = np.asarray(matrix[mask].mean(axis=0)).ravel()
        order = mean_scores.argsort()[::-1][:top_n]

        for rank, idx in enumerate(order, start=1):
            rows.append(
                {
                    group_column: group_value,
                    "rank": rank,
                    "term": feature_names[idx],
                    "mean_tfidf": float(mean_scores[idx]),
                }
            )

    return pd.DataFrame(rows)


def related_documents(
    frame: pd.DataFrame,
    matrix,
    neighbors: int = 3,
) -> pd.DataFrame:
    similarity = cosine_similarity(matrix)
    rows = []

    for i in range(len(frame)):
        candidates = np.argsort(similarity[i])[::-1]
        candidates = [j for j in candidates if j != i][:neighbors]

        for rank, j in enumerate(candidates, start=1):
            rows.append(
                {
                    "document_number": frame.iloc[i]["document_number"],
                    "related_document_number": frame.iloc[j]["document_number"],
                    "rank": rank,
                    "cosine_similarity": float(similarity[i, j]),
                    "related_title": frame.iloc[j]["title"],
                }
            )

    return pd.DataFrame(rows)


def cluster_documents(
    frame: pd.DataFrame,
    matrix,
    vectorizer: TfidfVectorizer,
    n_clusters: int = 9,
    top_n_terms: int = 12,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=20,
    )
    labels = model.fit_predict(matrix)

    assignments = frame[
        [
            "document_number",
            "publication_date",
            "document_type",
            "title",
            "agency_scopes",
        ]
    ].copy()
    assignments["cluster"] = labels

    features = np.array(vectorizer.get_feature_names_out())
    cluster_rows = []

    for cluster_id, center in enumerate(model.cluster_centers_):
        top_indices = center.argsort()[::-1][:top_n_terms]
        for rank, idx in enumerate(top_indices, start=1):
            cluster_rows.append(
                {
                    "cluster": cluster_id,
                    "rank": rank,
                    "term": features[idx],
                    "weight": float(center[idx]),
                }
            )

    return assignments, pd.DataFrame(cluster_rows)


def evaluate_cluster_counts(
    matrix,
    minimum_clusters: int = 5,
    maximum_clusters: int = 12,
) -> pd.DataFrame:
    rows = []

    for cluster_count in range(minimum_clusters, maximum_clusters + 1):
        model = KMeans(
            n_clusters=cluster_count,
            random_state=42,
            n_init=20,
        )
        labels = model.fit_predict(matrix)
        rows.append(
            {
                "clusters": cluster_count,
                "silhouette_cosine": float(
                    silhouette_score(matrix, labels, metric="cosine")
                ),
                "inertia": float(model.inertia_),
            }
        )

    return pd.DataFrame(rows)


def cluster_representatives(
    frame: pd.DataFrame,
    matrix,
    assignments: pd.DataFrame,
    n_clusters: int,
    representatives_per_cluster: int = 3,
) -> pd.DataFrame:
    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=20,
    )
    model.fit(matrix)
    distances = model.transform(matrix)
    rows = []

    for cluster_id in range(n_clusters):
        member_indices = np.flatnonzero(assignments["cluster"].to_numpy() == cluster_id)
        ordered = sorted(
            member_indices,
            key=lambda idx: distances[idx, cluster_id],
        )[:representatives_per_cluster]

        for rank, idx in enumerate(ordered, start=1):
            rows.append(
                {
                    "cluster": cluster_id,
                    "rank": rank,
                    "document_number": frame.iloc[idx]["document_number"],
                    "publication_date": frame.iloc[idx]["publication_date"],
                    "document_type": frame.iloc[idx]["document_type"],
                    "title": frame.iloc[idx]["title"],
                    "agency_scopes": frame.iloc[idx]["agency_scopes"],
                    "distance_to_centroid": float(distances[idx, cluster_id]),
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    frame = load_documents(database_url)
    frame["text"] = build_text(frame)
    frame["publication_year"] = pd.to_datetime(
        frame["publication_date"], errors="coerce"
    ).dt.year.astype("Int64")

    frame["nlp_scope"] = nlp_scope(frame)

    coverage = {
        "documents": int(len(frame)),
        "nonempty_title": int(frame["title"].fillna("").str.strip().ne("").sum()),
        "nonempty_abstract": int(frame["abstract"].fillna("").str.strip().ne("").sum()),
        "nonempty_text": int(frame["text"].str.strip().ne("").sum()),
        "administrative_information_collection": int(
            frame["nlp_scope"].eq("administrative_information_collection").sum()
        ),
        "substantive_policy": int(frame["nlp_scope"].eq("substantive_policy").sum()),
    }

    substantive = frame.loc[frame["nlp_scope"].eq("substantive_policy")].copy()
    substantive = substantive.reset_index(drop=True)

    vectorizer, matrix = fit_tfidf(substantive["text"])

    year_mask = substantive["publication_year"].notna().to_numpy()
    year_frame = substantive.loc[year_mask].copy()
    year_frame["publication_year"] = year_frame["publication_year"].astype(str)
    year_terms = top_terms_by_group(
        year_frame,
        matrix[year_mask],
        vectorizer,
        "publication_year",
    )

    agency_long = substantive.copy()
    agency_long["agency_scopes"] = agency_long["agency_scopes"].fillna("")
    exploded = agency_long.assign(
        agency_scope=agency_long["agency_scopes"].str.split(" | ", regex=False)
    ).explode("agency_scope")
    exploded = exploded[exploded["agency_scope"].ne("")]

    agency_rows = []
    features = np.array(vectorizer.get_feature_names_out())
    for scope in sorted(exploded["agency_scope"].unique()):
        doc_numbers = set(
            exploded.loc[
                exploded["agency_scope"] == scope,
                "document_number",
            ]
        )
        mask = substantive["document_number"].isin(doc_numbers).to_numpy()
        mean_scores = np.asarray(matrix[mask].mean(axis=0)).ravel()
        order = mean_scores.argsort()[::-1][:15]
        for rank, idx in enumerate(order, start=1):
            agency_rows.append(
                {
                    "agency_scope": scope,
                    "rank": rank,
                    "term": features[idx],
                    "mean_tfidf": float(mean_scores[idx]),
                }
            )
    agency_terms = pd.DataFrame(agency_rows)

    related = related_documents(substantive, matrix)
    selected_clusters = 9
    cluster_evaluation = evaluate_cluster_counts(matrix)
    assignments, cluster_terms = cluster_documents(
        substantive,
        matrix,
        vectorizer,
        n_clusters=selected_clusters,
    )
    representatives = cluster_representatives(
        substantive,
        matrix,
        assignments,
        n_clusters=selected_clusters,
    )

    frame[
        [
            "document_number",
            "publication_date",
            "document_type",
            "title",
            "agency_scopes",
            "nlp_scope",
            "text",
        ]
    ].to_csv(OUTPUT_DIR / "document_text.csv", index=False)

    frame[
        [
            "document_number",
            "publication_date",
            "document_type",
            "title",
            "abstract",
            "action",
            "effective_on",
            "comments_close_on",
            "citation",
            "agency_scopes",
            "cfr_references",
            "regulation_identifiers",
            "html_url",
            "pdf_url",
            "raw_text_url",
            "nlp_scope",
        ]
    ].to_csv(OUTPUT_DIR / "document_metadata.csv", index=False)
    year_terms.to_csv(OUTPUT_DIR / "top_terms_by_year.csv", index=False)
    agency_terms.to_csv(OUTPUT_DIR / "top_terms_by_agency.csv", index=False)
    related.to_csv(OUTPUT_DIR / "document_similarity.csv", index=False)
    assignments.to_csv(OUTPUT_DIR / "cluster_assignments.csv", index=False)
    cluster_terms.to_csv(OUTPUT_DIR / "cluster_terms.csv", index=False)
    cluster_evaluation.to_csv(OUTPUT_DIR / "cluster_evaluation.csv", index=False)
    representatives.to_csv(OUTPUT_DIR / "cluster_representatives.csv", index=False)

    metadata = {
        "coverage": coverage,
        "tfidf_features": int(matrix.shape[1]),
        "tfidf_documents": int(matrix.shape[0]),
        "tfidf_scope": "substantive_policy",
        "clusters": int(assignments["cluster"].nunique()),
        "cluster_selection": {
            "selected": selected_clusters,
            "evaluated_range": [5, 12],
            "criterion": "balance of cosine silhouette separation and policy interpretability",
        },
    }
    (OUTPUT_DIR / "nlp_summary.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
