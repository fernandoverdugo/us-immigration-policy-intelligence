from scripts.run_retrieval_benchmark import load_policy_documents, top_k_indices

import numpy as np


def test_top_k_indices_orders_scores_descending():
    scores = np.array([0.2, 0.9, 0.5, 0.1])
    result = top_k_indices(scores, 2)
    assert result.tolist() == [1, 2]


def test_policy_documents_use_stable_document_number_order():
    documents = load_policy_documents()
    assert documents["document_number"].tolist() == sorted(
        documents["document_number"].tolist()
    )
