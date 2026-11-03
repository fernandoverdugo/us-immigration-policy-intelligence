# U.S. Immigration Policy Intelligence

An API-driven data engineering, SQL, NLP, and semantic-search project for analyzing U.S. federal immigration policy activity in the Federal Register.

The project builds a reproducible 2017–2026 immigration-policy corpus, normalizes it into PostgreSQL, analyzes rulemaking patterns with SQL, explores policy topics with classical NLP, benchmarks semantic retrieval against TF-IDF, and exposes the resulting search system through FastAPI and a browser-based application.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/fernandoverdugo/us-immigration-policy-intelligence)

## Live application

**Public app:** https://us-immigration-policy-intelligence.onrender.com

**Interactive API docs:** https://us-immigration-policy-intelligence.onrender.com/docs

The service runs on Render's free web-service tier, so it may take roughly a minute to wake after a period of inactivity.

## Portfolio highlights

- **1,062** validated Federal Register documents in the current corpus
- **277** substantive policy documents used for topic-oriented NLP
- PostgreSQL relational model with agency, CFR, RIN, and corpus-evidence relationships
- Seven reusable SQL analyses covering activity, CFR references, RIN reuse, and rulemaking timelines
- TF-IDF text analysis, cosine similarity, K-means clustering, model-selection diagnostics, and representative-document review
- Nine analyst-interpreted policy clusters
- Local MiniLM sentence embeddings for semantic search
- Direct TF-IDF vs. semantic retrieval benchmark
- FastAPI backend with OpenAPI documentation
- Responsive browser search interface
- Docker packaging and end-to-end container validation
- GitHub Actions for database, corpus, NLP, retrieval, API, and container checks

## Research questions

The project is designed to explore questions such as:

- How has scoped federal immigration-policy activity changed over time?
- Which agencies and regulatory provisions appear most frequently?
- Which proposed and final rules can be connected through Regulation Identifier Numbers?
- How long do linked rulemaking actions take to move from proposal to final rule?
- What recurring policy topics emerge from the regulatory corpus?
- Can semantic search retrieve useful policy documents more effectively than lexical TF-IDF search?

## Data source

The project retrieves Federal Register metadata through the public FederalRegister.gov API.

Initial agency scope:

- U.S. Citizenship and Immigration Services (USCIS)
- U.S. Customs and Border Protection (CBP)
- U.S. Immigration and Customs Enforcement (ICE)
- Executive Office for Immigration Review (EOIR)

Agency membership alone is not treated as sufficient evidence of immigration-policy relevance. Corpus inclusion uses auditable signals such as Title 8 CFR references, controlled immigration terminology, and scoped agency rules.

Raw API responses remain separate from the normalized analytical corpus so the inclusion methodology can be reviewed and revised.

## Corpus

Current validated corpus:

| Measure | Count |
| --- | ---: |
| Unique Federal Register documents | 1,062 |
| Rules | 66 |
| Proposed Rules | 31 |
| Notices | 965 |
| Substantive policy documents used for topic NLP | 277 |
| Routine administrative information-collection notices | 785 |

The corpus distinguishes formal **core rulemaking** (Rules and Proposed Rules) from the larger **supplemental notice** layer.

## Architecture

```text
Federal Register API
        ↓
auditable corpus selection
        ↓
raw JSON snapshots
        ↓
normalization + validation
        ↓
PostgreSQL
   ↙             ↘
SQL analytics    classical NLP
                      ↓
                   TF-IDF
                      ↓
              semantic embeddings
                      ↓
              retrieval benchmark
                      ↓
                   FastAPI
                      ↓
              web search interface
```

## PostgreSQL and SQL analytics

The normalized database preserves:

- documents
- issuing agencies
- many-to-many document/agency relationships
- CFR references
- Regulation Identifier Numbers (RINs)
- corpus-selection evidence

The SQL analytical layer includes:

1. annual activity by document type
2. activity by scoped agency
3. most frequently referenced CFR parts
4. RIN reuse across documents
5. proposed-rule to final-rule timing
6. genuine multi-agency scoped documents
7. year-over-year activity change

Compact generated outputs are retained under `analysis/outputs/`.

### Selected SQL findings

- Core rulemaking peaks at **20 Rules + Proposed Rules in 2020** within the current corpus.
- Overall scoped activity reaches **137 documents in 2023**.
- **56 RINs** appear across multiple corpus documents.
- **16 RINs** contain both a Proposed Rule and a later Rule.
- Proposal-to-final intervals for those linked RINs range from **82 to 714 days**, with a **median of 200 days**.
- Only **3 documents** span more than one of the project's four agency scopes.

See `analysis/README.md` for interpretation and limitations.

## Classical NLP

Topic-oriented NLP excludes routine information-collection notices while preserving them in the underlying corpus.

Methods include:

- normalized title + abstract text
- unigram and bigram TF-IDF
- distinctive terms by year and agency
- cosine-similarity document retrieval
- K-means clustering
- cosine-silhouette model evaluation
- representative-document inspection

The selected **9-cluster** solution balances quantitative separation with policy interpretability.

Interpreted themes include:

- Deferred Enforced Departure and employment authorization
- asylum, removal, and broader immigration rulemaking
- Western Hemisphere Travel Initiative / tribal entry credentials
- Temporary Protected Status extensions and redesignations
- EOIR / Board of Immigration Appeals procedure
- F-1 student severe-economic-hardship employment authorization
- TPS employment-authorization continuity
- immigration fees and civil penalties
- TPS terminations

These are exploratory analyst interpretations, not official Federal Register classifications.

See `analysis/nlp/FINDINGS.md`.

## Semantic retrieval

The project compares TF-IDF retrieval against local sentence embeddings using:

`sentence-transformers/all-MiniLM-L6-v2`

Nine natural-language policy queries are evaluated against the same 277-document substantive-policy corpus.

| Metric | TF-IDF | Semantic |
| --- | ---: | ---: |
| Mean precision@5 | 0.733 | **0.844** |
| Hit rate@5 | **1.000** | **1.000** |
| Mean reciprocal rank@5 | 0.889 | **0.917** |

The benchmark uses analyst-interpreted topic clusters as a relevance proxy. It is useful for comparing retrieval behavior but is not a formal legal relevance judgment.

See `analysis/retrieval/FINDINGS.md`.

## Application

FastAPI exposes:

- `GET /` — browser search interface
- `GET /health` — service status
- `GET /topics` — interpreted policy topics
- `GET /search?q=<query>&k=<n>` — semantic policy search
- `GET /documents/{document_number}` — document metadata
- `GET /docs` — interactive OpenAPI documentation

Search results include:

- Federal Register title
- publication date
- document type
- scoped agency
- analyst-interpreted topic
- semantic similarity score
- direct link to the source document on FederalRegister.gov

## Repository structure

```text
.
├── .github/workflows/
├── analysis/
│   ├── nlp/
│   ├── outputs/
│   └── retrieval/
├── api/
├── data/
├── database/
│   └── queries/
├── scripts/
├── src/
│   ├── ingestion/
│   └── retrieval/
├── tests/
├── web/
├── Dockerfile
├── DEPLOYMENT.md
├── render.yaml
├── requirements.txt
├── requirements-api.txt
├── requirements-retrieval.txt
└── README.md
```

## Local analytical workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m scripts.fetch_federal_register
python -m scripts.load_postgres
python -m scripts.run_sql_analysis
python -m scripts.run_nlp_analysis
```

PostgreSQL requires `DATABASE_URL`; see `database/README.md`.

## Local application

Install the application dependencies:

```bash
python -m pip install -r requirements-api.txt
```

Run:

```bash
uvicorn api.main:app --reload
```

Then open:

- `http://localhost:8000/`
- `http://localhost:8000/docs`

## Docker

```bash
docker build -t immigration-policy-intelligence .
docker run --rm -p 8000:8000 immigration-policy-intelligence
```

The deployment image installs CPU-only PyTorch because the application performs inference on CPU and does not require CUDA.

See `DEPLOYMENT.md` for Render deployment instructions.

## Reproducibility and CI

GitHub Actions validates:

- corpus selection
- Python tests
- PostgreSQL schema and relational loading
- SQL analytical outputs
- NLP outputs and model selection
- TF-IDF vs. semantic retrieval benchmark
- real semantic search execution
- FastAPI/OpenAPI behavior
- Docker image build and live-container HTTP checks

## Methodological boundaries

- The corpus is a scoped analytical sample defined by explicit inclusion rules, not a claim to contain every immigration-related federal policy action.
- Counts are descriptive and should not be interpreted as causal measures of policy intensity.
- RIN linkage is useful for tracing regulatory actions but may not capture every legally relevant procedural stage.
- NLP clusters are exploratory.
- Retrieval benchmark labels are topic proxies, not attorney-reviewed relevance judgments.
- For authoritative legal research, users should verify all source material against the official Federal Register publication.

## Technologies

Python · PostgreSQL · SQL · pandas · NumPy · scikit-learn · sentence-transformers · PyTorch · FastAPI · Uvicorn · HTML/CSS/JavaScript · Docker · pytest · GitHub Actions
