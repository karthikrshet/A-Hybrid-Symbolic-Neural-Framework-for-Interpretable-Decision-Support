"""Multi-Criteria Decision Analysis (MCDA) scoring routines for decision fusion."""

import numpy as np
from typing import Dict, List

def calculate_topsis_score(neural_score: float, rule_severity_score: float, weight_neural: float = 0.60, weight_symbolic: float = 0.40) -> float:
    """Calculates TOPSIS composite risk index from normalized criteria."""
    # Normalization
    norm_n = neural_score / (np.sqrt(neural_score**2 + 1e-6))
    norm_s = rule_severity_score / (np.sqrt(rule_severity_score**2 + 1e-6))
    
    # Weighted criteria
    w_n = norm_n * weight_neural
    w_s = norm_s * weight_symbolic
    
    # Ideal positive and negative
    ideal_best = np.array([weight_neural, weight_symbolic])
    ideal_worst = np.array([0.0, 0.0])
    
    crit = np.array([w_n, w_s])
    d_plus = np.linalg.norm(crit - ideal_best)
    d_minus = np.linalg.norm(crit - ideal_worst)
    
    closeness = d_minus / (d_plus + d_minus + 1e-6)
    return float(np.clip(closeness, 0.0, 1.0))
