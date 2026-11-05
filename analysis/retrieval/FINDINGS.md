# Retrieval findings

The current retrieval benchmark compares lexical TF-IDF search with local FastEmbed/ONNX sentence embeddings over the substantive-policy corpus.

## Current benchmark snapshot

At the current committed snapshot, the benchmark contains **9 natural-language queries** evaluated against **277 substantive policy documents**. The document count can change as the scheduled Federal Register refresh updates the corpus.

| Metric | TF-IDF | Semantic embeddings |
|---|---:|---:|
| Mean precision@5 | 0.733 | **0.844** |
| Hit rate@5 | **1.000** | **1.000** |
| Mean reciprocal rank@5 | 0.889 | **0.917** |

The semantic model improves mean precision@5 by about **15.2% relative to TF-IDF** and also improves mean reciprocal rank.

## Where semantic retrieval helps most

Semantic retrieval substantially improves several paraphrased policy queries:

- **DED / Liberian work authorization:** precision@5 improves from 0.8 to 1.0.
- **Asylum / withholding of removal:** precision@5 improves from 0.6 to 0.8.
- **TPS + employment authorization:** precision@5 improves from 0.2 to 0.8.
- **TPS termination:** precision@5 improves from 0.4 to 0.8.

For the TPS employment-authorization query, the semantic model retrieves documents such as *Automatic Extension of Employment Authorization Documentation for Beneficiaries Under El Salvador's Designation for Temporary Protected Status* at rank 1, whereas TF-IDF mixes extension, termination, and redesignation notices.

## Where the benchmark proxy is imperfect

The query *extension and redesignation of temporary protected status* scores worse under the cluster-based semantic metric.

This does not necessarily indicate worse practical retrieval. The semantic results include multiple closely related TPS documents assigned to neighboring exploratory clusters such as TPS extension, employment-authorization continuity, and correction notices.

The benchmark therefore evaluates **topic alignment against analyst-interpreted clusters**, not legal or human relevance judgments. Closely related policy subtopics can be penalized even when the returned document would be useful to a researcher.

## Decision

Semantic retrieval is the primary natural-language search method because it:

1. improves aggregate precision and reciprocal rank,
2. handles paraphrased queries better than lexical matching,
3. preserves 100% hit rate@5 in the current benchmark, and
4. produces qualitatively stronger results for several important policy topics.

TF-IDF remains useful as a transparent lexical baseline and may later be combined with semantic retrieval in a hybrid ranker.

## Model

`sentence-transformers/all-MiniLM-L6-v2`

The model runs locally through FastEmbed's ONNX runtime and does not require a paid API. The benchmark and deployed search service use the same embedding implementation.

## Evaluation limitation

The nine-query benchmark is deliberately small and topic-oriented. A stronger production-style evaluation would use manually judged query-document relevance labels rather than exploratory cluster membership alone.
