import numpy as np
import pandas as pd
import pytest

from src.retrieval.search import filter_mask, make_snippet, semantic_search


def test_semantic_search_rejects_empty_query():
    with pytest.raises(ValueError, match="must not be empty"):
        semantic_search("   ")


def test_semantic_search_rejects_invalid_k():
    with pytest.raises(ValueError, match="between 1 and 50"):
        semantic_search("asylum", 0)


def test_make_snippet_truncates_cleanly():
    text = "word " * 100
    snippet = make_snippet(text, limit=40)
    assert snippet.endswith("…")
    assert len(snippet) <= 41


def test_filter_mask_combines_fields():
    frame = pd.DataFrame(
        {
            "publication_date": ["2024-01-01", "2023-06-01"],
            "agency_scopes": ["uscis", "eoir | uscis"],
            "document_type": ["Notice", "Rule"],
            "cluster": [3, 4],
        }
    )

    mask = filter_mask(
        frame,
        year=2024,
        agency="uscis",
        document_type="Notice",
        topic=3,
    )

    assert np.array_equal(mask, np.array([True, False]))
