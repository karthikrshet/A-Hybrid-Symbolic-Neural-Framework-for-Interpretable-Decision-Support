"""Compare the conventional neural network with the hybrid neuro-symbolic framework.

Run from the ``backend`` folder:  python experiments/evaluate_baseline_vs_hybrid.py
Results are written to experiments/results/<domain>.json and shown in the UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.domain_manager import domain_manager  # noqa: E402
from app.core.evaluation import evaluate_domain  # noqa: E402

COLS = ("accuracy", "precision", "recall", "f1", "hard_rule_consistency", "soft_rule_agreement", "avg_evidence_items")

if __name__ == "__main__":
    for d in domain_manager.list():
        run = evaluate_domain(d.id)
        print(f"\n=== {run.domain_name} ({run.test_samples} test cases) ===")
        print(f"{'system':<26}" + "".join(f"{c[:12]:>14}" for c in COLS))
        for s in ("neural", "symbolic", "hybrid"):
            m = run.systems[s]
            print(f"{m['name']:<26}" + "".join(f"{m[c]:>14.3f}" for c in COLS))
