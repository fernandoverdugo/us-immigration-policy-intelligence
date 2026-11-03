# FastAPI service

The API exposes the policy-intelligence retrieval layer as a reusable application service.

## Endpoints

### `GET /health`

Returns service status, indexed document count, semantic retrieval model, and deployed Render commit when available.

### `GET /topics`

Returns the nine analyst-interpreted exploratory policy topics.

### `GET /filters`

Returns available:

- agencies
- publication years
- document types
- interpreted policy topics

### `GET /search?q=<query>&k=<results>`

Runs natural-language semantic search over the substantive Federal Register policy corpus.

Optional filters:

- `year`
- `agency`
- `document_type`
- `topic`

Search results include an abstract snippet, topic label, similarity score, internal detail-page URL, and official Federal Register URL.

### `GET /documents/{document_number}`

Returns rich indexed metadata for one Federal Register document, including:

- title and abstract
- agency action
- publication/effective/comment-close dates
- Federal Register citation
- scoped agencies
- CFR references
- Regulation Identifier Numbers
- official HTML/PDF/raw-text links
- three related documents from the TF-IDF similarity index

### `GET /document/{document_number}`

Serves the browser-based document-detail page.

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
