# NLP findings

The classical NLP layer uses the full Federal Register corpus for coverage reporting, then separates routine administrative information-collection notices from topic-oriented policy analysis.

## Current analytical snapshot

- Full corpus: **1,062 documents**
- Routine administrative information-collection notices: **785**
- Substantive policy subset: **277**
- TF-IDF features: **2,276**
- Selected K-means clusters: **9**

These counts describe the current committed snapshot and can change as the scheduled Federal Register refresh updates the corpus.

The 9-cluster solution was selected as a balance between cosine-silhouette separation and policy interpretability. The pipeline evaluates cluster counts from 5 through 12 and preserves the evaluation table.

## Interpreted clusters

| Cluster | Documents | Analyst interpretation |
|---|---:|---|
| 0 | 30 | Deferred Enforced Departure (DED) and related employment authorization |
| 1 | 59 | Asylum, removal, border, and broader immigration rulemaking |
| 2 | 6 | Western Hemisphere Travel Initiative and tribal entry credentials |
| 3 | 32 | Temporary Protected Status extensions and redesignations |
| 4 | 35 | EOIR / Board of Immigration Appeals procedure and adjudication |
| 5 | 31 | F-1 nonimmigrant student severe-economic-hardship employment authorization |
| 6 | 22 | TPS extensions and employment-authorization continuity |
| 7 | 37 | Immigration fees, penalties, and inflation adjustments |
| 8 | 25 | TPS terminations |

These labels are analyst interpretations of exploratory clusters. They are not official Federal Register policy classifications.

## Representative examples

- Cluster 0 includes DED employment-authorization notices for Liberia and Palestinians.
- Cluster 1 includes major asylum and withholding-of-removal rules.
- Cluster 2 groups Western Hemisphere Travel Initiative notices involving approved Native American tribal cards.
- Cluster 3 groups TPS extension and redesignation notices.
- Cluster 4 groups EOIR electronic filing, appellate procedure, and organizational rules.
- Cluster 5 groups F-1 student severe-economic-hardship employment-authorization notices.
- Cluster 6 groups TPS extension notices with employment-authorization continuity.
- Cluster 7 groups immigration-fee and civil-penalty inflation adjustments.
- Cluster 8 groups TPS termination notices.

## Agency language patterns

The TF-IDF agency summaries show strong substantive differentiation:

- **CBP:** entry, travel, border, ports, penalties
- **EOIR:** rule, immigration, asylum, appeals, review
- **ICE:** nonimmigrant students, economic hardship
- **USCIS:** TPS, designation, protected status, extension

## Model-selection note

Cosine silhouette scores increased from approximately **0.163 at 5 clusters** to a peak of approximately **0.233 at 11 clusters** within the tested range. The 9-cluster solution scored approximately **0.197** but produced a more compact and policy-coherent taxonomy.

For this exploratory analysis, interpretability is treated as an explicit model-selection criterion rather than maximizing silhouette score alone.

## Reproducibility

The NLP workflow rebuilds the corpus, loads PostgreSQL, constructs analytical text, evaluates cluster counts, generates TF-IDF outputs, computes document similarities, selects representative documents, and publishes the resulting artifacts.

The generated files under `analysis/nlp/results/` are reproducible outputs from that workflow.
