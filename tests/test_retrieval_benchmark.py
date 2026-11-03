from scripts.run_retrieval_benchmark import top_k_indices

import numpy as np


def test_top_k_indices_orders_scores_descending():
    scores = np.array([0.2, 0.9, 0.5, 0.1])
    result = top_k_indices(scores, 2)
    assert result.tolist() == [1, 2]
