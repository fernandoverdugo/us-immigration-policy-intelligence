# Milestone 5 — Semantic retrieval

This stage compares the project's existing TF-IDF retrieval baseline with local sentence embeddings.

## Embedding model

The workflow uses:

`sentence-transformers/all-MiniLM-L6-v2`

Embeddings are generated locally in GitHub Actions. No paid API or external model-serving credential is required.

## Evaluation design

The benchmark contains nine natural-language queries corresponding to the nine analyst-interpreted policy clusters from Milestone 4.

For each query, the project compares TF-IDF and semantic retrieval using:

- precision@5
- hit rate@5
- reciprocal rank@5

The target cluster is used as a topic-level relevance proxy. This is useful for comparing retrieval behavior, but it is not a legal relevance judgment and should not be interpreted as a formal information-retrieval gold standard.

## Outputs

- `semantic_embeddings.npy`
- `embedding_index.csv`
- `benchmark_results.csv`
- `retrieval_examples.csv`
- `retrieval_summary.json`

The benchmark must outperform or meaningfully complement the lexical baseline before semantic retrieval is promoted into the application layer.


## Upstream dependency

The retrieval benchmark consumes the committed Milestone 4 outputs in `analysis/nlp/results/`, including the normalized `document_text.csv` index and cluster assignments. This ensures lexical and semantic retrieval are evaluated against the same validated substantive-policy corpus.
