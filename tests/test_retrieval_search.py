from src.retrieval.search import semantic_search

import pytest


def test_semantic_search_rejects_empty_query():
    with pytest.raises(ValueError, match="must not be empty"):
        semantic_search("   ")


def test_semantic_search_rejects_invalid_k():
    with pytest.raises(ValueError, match="between 1 and 50"):
        semantic_search("asylum", 0)
