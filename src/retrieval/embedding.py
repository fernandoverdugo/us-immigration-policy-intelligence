from __future__ import annotations

import os
from pathlib import Path
from typing import Any

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CACHE_DIR = Path("fastembed_cache")


def embedding_cache_dir() -> Path:
    return Path(os.environ.get("FASTEMBED_CACHE_PATH", DEFAULT_CACHE_DIR))


def create_embedding_model(
    *,
    local_files_only: bool | None = None,
) -> Any:
    from fastembed import TextEmbedding

    if local_files_only is None:
        local_files_only = os.environ.get("FASTEMBED_LOCAL_FILES_ONLY") == "1"

    return TextEmbedding(
        model_name=MODEL_NAME,
        cache_dir=str(embedding_cache_dir()),
        threads=1,
        local_files_only=local_files_only,
    )
