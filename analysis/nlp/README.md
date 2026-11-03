# Milestone 4 — Classical NLP

This stage analyzes the Federal Register corpus using interpretable text methods before introducing embeddings.

## NLP scope

The full Federal Register corpus remains available for database and SQL analysis. For topic-oriented NLP, the pipeline separates routine administrative information-collection notices from substantive policy documents.

A document is classified as `administrative_information_collection` when it is a Notice whose title begins with `Agency Information Collection Activities`.

All Rules, Proposed Rules, and other notices are classified as `substantive_policy`.

In the current corpus, this leaves approximately 288 substantive documents for TF-IDF, similarity analysis, and clustering, while retaining the administrative notices in the underlying corpus.

## Methods

- title + abstract analytical text construction
- TF-IDF with unigram and bigram features
- distinctive terms by year
- distinctive terms by scoped agency
- cosine-similarity document retrieval
- K-means clustering
- cluster-term inspection

## Outputs

The workflow writes:

- `document_text.csv`
- `top_terms_by_year.csv`
- `top_terms_by_agency.csv`
- `document_similarity.csv`
- `cluster_assignments.csv`
- `cluster_terms.csv`
- `nlp_summary.json`

The clustering step is exploratory. Cluster IDs are not treated as authoritative policy categories until their terms and representative documents are manually inspected.
