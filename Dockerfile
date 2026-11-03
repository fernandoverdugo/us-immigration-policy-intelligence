FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8000
ENV FASTEMBED_CACHE_PATH=/opt/fastembed-cache
ENV FASTEMBED_LOCAL_FILES_ONLY=1

COPY requirements.txt requirements-api.txt ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-api.txt \
    && python - <<'PY'
from fastembed import TextEmbedding
TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir="/opt/fastembed-cache",
    threads=1,
)
PY

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
