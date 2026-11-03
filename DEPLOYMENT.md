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


## Render

The repository includes a `render.yaml` Blueprint for a Docker-based web service.

Current Blueprint settings:

- Docker runtime
- free web-service plan
- `/health` health check
- auto-deploy only after repository checks pass
- application port `8000`

Render's free web services are suitable for portfolio/demo use, but they spin down after 15 minutes without inbound traffic and can take roughly a minute to wake on the next request. The free plan currently provides 512 MB RAM, so the deployment image installs CPU-only PyTorch to reduce unnecessary CUDA dependencies and memory/storage overhead.

To deploy manually in Render:

1. Create a new Blueprint or Web Service from this GitHub repository.
2. Allow Render to read the repository's `render.yaml`.
3. Confirm the service name and Free compute plan.
4. Deploy.
5. Verify `/health`, `/`, and `/docs` on the generated `onrender.com` URL.

The service does not require a database or secret API key at runtime because it serves the committed analytical index and computes only the query embedding on demand.
