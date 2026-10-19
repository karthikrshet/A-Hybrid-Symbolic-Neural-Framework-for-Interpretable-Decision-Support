import numpy as np
from ml.evaluation.metrics import compute_brier_score, compute_expected_calibration_error

def test_brier_score():
    y_true = np.array([1, 0, 1, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.2])
    score = compute_brier_score(y_true, y_prob)
    assert 0.0 <= score <= 0.2

def test_ece_metric():
    y_true = np.array([1, 0, 1, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.2])
    ece = compute_expected_calibration_error(y_true, y_prob, n_bins=5)
    assert 0.0 <= ece <= 1.0
