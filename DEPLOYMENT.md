# Application deployment

The repository runs as a single Docker container serving both the FastAPI backend and browser interface.

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
precomputed FastEmbed document embeddings
        +
FastEmbed / ONNX MiniLM query encoder
```

The application uses `sentence-transformers/all-MiniLM-L6-v2` through FastEmbed's ONNX runtime. The deployment image installs the fully resolved environment from `requirements-lock.txt`. The document and query embedding paths use the same implementation.

The ONNX model is downloaded during the Docker build into `/opt/fastembed-cache`. Runtime inference is configured for local-files-only operation, so a cold application start does not depend on downloading model weights from an external model host.

The deployed service uses committed analytical indexes and therefore does not require a live PostgreSQL database. PostgreSQL remains the analytical source of truth for ingestion and SQL analysis.

## Render

The repository includes a `render.yaml` Blueprint aligned with the deployed service:

- Docker runtime
- Free web-service plan
- Ohio region
- auto-deploy configured for commits to `main`
- application port `8000`

The connected Render service was created directly rather than from the Blueprint, so Render itself does not currently have a platform-level health-check path configured. Application health is instead verified through the public `/health` endpoint by the GitHub live smoke-test workflow.

Public application:

`https://us-immigration-policy-intelligence.onrender.com`

Interactive API docs:

`https://us-immigration-policy-intelligence.onrender.com/docs`

The Free service can spin down after inactivity. The GitHub live smoke-test workflow retries the public service to allow for cold starts, runs automatically after successful container validation on `main`, and rejects stale deployments by comparing Render's `RENDER_GIT_COMMIT` value with the current GitHub `main` SHA.

The service does not require runtime secrets or a database connection.
