# Application deployment

The repository can run as a single container serving both the FastAPI backend and the web interface.

## Container

Build:

```bash
docker build -t immigration-policy-intelligence .
```

Run:

```bash
docker run --rm -p 8000:8000 immigration-policy-intelligence
```

Open:

- Web application: `http://localhost:8000/`
- Interactive API docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`

## Runtime architecture

```text
Browser
  ↓
FastAPI
  ├── static web application
  ├── semantic /search endpoint
  ├── document metadata endpoint
  └── OpenAPI documentation
        ↓
precomputed document embeddings
        +
local MiniLM query encoder
```

The current deployed-service design uses committed analytical indexes so the app can run without requiring a live PostgreSQL instance. PostgreSQL remains the project's analytical source of truth for ingestion and SQL analysis.

A future production deployment could replace the file-backed search metadata with PostgreSQL while retaining the same API contract.
