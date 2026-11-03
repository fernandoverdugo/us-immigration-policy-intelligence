# Milestone 4 — Classical NLP

This stage analyzes the Federal Register corpus using interpretable text methods before introducing embeddings.

## NLP scope

The full Federal Register corpus remains available for database and SQL analysis. For topic-oriented NLP, the pipeline separates routine administrative information-collection notices from substantive policy documents.

A Notice is classified as `administrative_information_collection` when its title or abstract contains `information collection` or `Paperwork Reduction Act`.

All Rules, Proposed Rules, and other notices are classified as `substantive_policy`.

The current corpus contains 1,062 documents. The refined topic-analysis subset contains roughly 277 substantive documents.

## Methods

- title + abstract analytical text construction
- TF-IDF with unigram and bigram features
- distinctive terms by year
- distinctive terms by scoped agency
- cosine-similarity document retrieval
- K-means clustering
- cosine-silhouette evaluation across 5–12 clusters
- representative-document extraction for each cluster

The selected 9-cluster solution balances quantitative separation with policy interpretability. The cluster-evaluation table is retained so this choice remains auditable.

## Outputs

The workflow writes:

- `document_text.csv`
- `top_terms_by_year.csv`
- `top_terms_by_agency.csv`
- `document_similarity.csv`
- `cluster_assignments.csv`
- `cluster_terms.csv`
- `cluster_evaluation.csv`
- `cluster_representatives.csv`
- `nlp_summary.json`

Cluster IDs are exploratory analytical groupings, not official policy categories.
