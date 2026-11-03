# FastAPI service

The API exposes the policy-intelligence retrieval layer as a reusable application service.

## Endpoints

### `GET /health`

Returns service status, indexed document count, and the semantic retrieval model.

### `GET /search?q=<query>&k=<results>`

Runs natural-language semantic search over the substantive Federal Register policy corpus.

Parameters:

- `q` — natural-language query
- `k` — number of results, 1–50

### `GET /documents/{document_number}`

Returns indexed metadata for one Federal Register document.

## Local development

Install retrieval and API dependencies:

```bash
python -m pip install -r requirements-retrieval.txt
```

Run:

```bash
uvicorn api.main:app --reload
```

FastAPI automatically exposes interactive API documentation at `/docs` and an OpenAPI schema at `/openapi.json`.

The sentence-transformer model is loaded lazily when semantic search is first invoked. Health and document metadata endpoints do not require loading the model.
