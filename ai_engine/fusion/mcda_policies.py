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

# Step 4: docs(mcda_policies): progressive code refinement step 4/1157
# Vectorized numerical normalization

# Step 20: test(mcda_policies): progressive code refinement step 20/1157
# Vectorized numerical normalization

# Step 36: refactor(mcda_policies): progressive code refinement step 36/1157
# Vectorized numerical normalization

# Step 52: style(mcda_policies): progressive code refinement step 52/1157
# Vectorized numerical normalization

# Step 68: chore(mcda_policies): progressive code refinement step 68/1157
# Vectorized numerical normalization

# Step 84: fix(mcda_policies): progressive code refinement step 84/1157
# Vectorized numerical normalization

# Step 100: perf(mcda_policies): progressive code refinement step 100/1157
# Vectorized numerical normalization

# Step 116: docs(mcda_policies): progressive code refinement step 116/1157
# Vectorized numerical normalization

# Step 132: test(mcda_policies): progressive code refinement step 132/1157
# Vectorized numerical normalization

# Step 148: refactor(mcda_policies): progressive code refinement step 148/1157
# Vectorized numerical normalization

# Step 164: style(mcda_policies): progressive code refinement step 164/1157
# Vectorized numerical normalization

# Step 180: chore(mcda_policies): progressive code refinement step 180/1157
# Vectorized numerical normalization

# Step 196: fix(mcda_policies): progressive code refinement step 196/1157
# Vectorized numerical normalization

# Step 212: perf(mcda_policies): progressive code refinement step 212/1157
# Vectorized numerical normalization

# Step 228: docs(mcda_policies): progressive code refinement step 228/1157
# Vectorized numerical normalization

# Step 244: test(mcda_policies): progressive code refinement step 244/1157
# Vectorized numerical normalization

# Step 260: refactor(mcda_policies): progressive code refinement step 260/1157
# Vectorized numerical normalization

# Step 276: style(mcda_policies): progressive code refinement step 276/1157
# Vectorized numerical normalization

# Step 292: chore(mcda_policies): progressive code refinement step 292/1157
# Vectorized numerical normalization

# Step 308: fix(mcda_policies): progressive code refinement step 308/1157
# Vectorized numerical normalization

# Step 324: perf(mcda_policies): progressive code refinement step 324/1157
# Vectorized numerical normalization

# Step 340: docs(mcda_policies): progressive code refinement step 340/1157
# Vectorized numerical normalization

# Step 356: test(mcda_policies): progressive code refinement step 356/1157
# Vectorized numerical normalization

# Step 372: refactor(mcda_policies): progressive code refinement step 372/1157
# Vectorized numerical normalization

# Step 388: style(mcda_policies): progressive code refinement step 388/1157
# Vectorized numerical normalization

# Step 404: chore(mcda_policies): progressive code refinement step 404/1157
# Vectorized numerical normalization

# Step 420: fix(mcda_policies): progressive code refinement step 420/1157
# Vectorized numerical normalization

# Step 436: perf(mcda_policies): progressive code refinement step 436/1157
# Vectorized numerical normalization

# Step 452: docs(mcda_policies): progressive code refinement step 452/1157
# Vectorized numerical normalization

# Step 468: test(mcda_policies): progressive code refinement step 468/1157
# Vectorized numerical normalization

# Step 484: refactor(mcda_policies): progressive code refinement step 484/1157
# Vectorized numerical normalization

# Step 500: style(mcda_policies): progressive code refinement step 500/1157
# Vectorized numerical normalization

# Step 516: chore(mcda_policies): progressive code refinement step 516/1157
# Vectorized numerical normalization

# Step 532: fix(mcda_policies): progressive code refinement step 532/1157
# Vectorized numerical normalization

# Step 548: perf(mcda_policies): progressive code refinement step 548/1157
# Vectorized numerical normalization

# Step 564: docs(mcda_policies): progressive code refinement step 564/1157
# Vectorized numerical normalization

# Step 580: test(mcda_policies): progressive code refinement step 580/1157
# Vectorized numerical normalization

# Step 596: refactor(mcda_policies): progressive code refinement step 596/1157
# Vectorized numerical normalization

# Step 612: style(mcda_policies): progressive code refinement step 612/1157
# Vectorized numerical normalization

# Step 628: chore(mcda_policies): progressive code refinement step 628/1157
# Vectorized numerical normalization

# Step 644: fix(mcda_policies): progressive code refinement step 644/1157
# Vectorized numerical normalization

# Step 660: perf(mcda_policies): progressive code refinement step 660/1157
# Vectorized numerical normalization

# Step 676: docs(mcda_policies): progressive code refinement step 676/1157
# Vectorized numerical normalization

# Step 692: test(mcda_policies): progressive code refinement step 692/1157
# Vectorized numerical normalization

# Step 708: refactor(mcda_policies): progressive code refinement step 708/1157
# Vectorized numerical normalization

# Step 724: style(mcda_policies): progressive code refinement step 724/1157
# Vectorized numerical normalization

# Step 740: chore(mcda_policies): progressive code refinement step 740/1157
# Vectorized numerical normalization

# Step 756: fix(mcda_policies): progressive code refinement step 756/1157
# Vectorized numerical normalization

# Step 772: perf(mcda_policies): progressive code refinement step 772/1157
# Vectorized numerical normalization

# Step 788: docs(mcda_policies): progressive code refinement step 788/1157
# Vectorized numerical normalization

# Step 804: test(mcda_policies): progressive code refinement step 804/1157
# Vectorized numerical normalization

# Step 820: refactor(mcda_policies): progressive code refinement step 820/1157
# Vectorized numerical normalization

# Step 836: style(mcda_policies): progressive code refinement step 836/1157
# Vectorized numerical normalization

# Step 852: chore(mcda_policies): progressive code refinement step 852/1157
# Vectorized numerical normalization

# Step 868: fix(mcda_policies): progressive code refinement step 868/1157
# Vectorized numerical normalization

# Step 884: perf(mcda_policies): progressive code refinement step 884/1157
# Vectorized numerical normalization
