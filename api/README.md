# FastAPI service

The API exposes the policy-intelligence retrieval layer as a reusable application service.

## Endpoints

### `GET /health`

Returns service status, indexed document count, and semantic retrieval model.

### `GET /topics`

Returns the nine analyst-interpreted exploratory policy topics.

### `GET /search?q=<query>&k=<results>`

Runs natural-language semantic search over the substantive Federal Register policy corpus.

Parameters:

- `q` — natural-language query
- `k` — number of results, 1–50

### `GET /documents/{document_number}`

Returns indexed metadata for one Federal Register document.

## Local development

Install application dependencies:

```bash
python -m pip install -r requirements-api.txt
```

Run:

```bash
uvicorn api.main:app --reload
```

FastAPI automatically exposes interactive API documentation at `/docs` and an OpenAPI schema at `/openapi.json`.

## Retrieval runtime

The application uses FastEmbed/ONNX with `sentence-transformers/all-MiniLM-L6-v2`. Model creation is lazy within the Python process. The Docker deployment preloads the model files during image construction and runs with local-files-only inference.
