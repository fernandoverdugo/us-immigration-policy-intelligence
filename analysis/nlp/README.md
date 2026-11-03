# Milestone 4 — Classical NLP

This stage analyzes the Federal Register corpus using interpretable text methods before introducing embeddings.

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
