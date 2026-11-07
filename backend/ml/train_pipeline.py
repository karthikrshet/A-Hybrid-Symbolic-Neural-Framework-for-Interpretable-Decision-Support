"""Train the neural model of every domain and run the hybrid-vs-baseline benchmark.

Usage (from the ``backend`` folder):
    python ml/train_pipeline.py              # all domains
    python ml/train_pipeline.py finance      # one domain
    python ml/train_pipeline.py --fresh      # regenerate datasets too
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import DATASET_DIR  # noqa: E402
from app.core.domain_manager import domain_manager  # noqa: E402
from app.core.evaluation import evaluate_domain  # noqa: E402


def main(argv: list[str]) -> None:
    fresh = "--fresh" in argv
    wanted = [a for a in argv if not a.startswith("--")] or [d.id for d in domain_manager.list()]
    for domain_id in wanted:
        if fresh:
            for f in DATASET_DIR.glob(f"{domain_id}*.csv"):
                f.unlink()
        bundle = domain_manager.train(domain_id)
        meta = bundle.metadata
        run = evaluate_domain(domain_id)
        n, h = run.systems["neural"], run.systems["hybrid"]
        print(
            f"{domain_id:<20} epochs={meta['epochs']:<4} "
            f"neural acc={n['accuracy']:.3f} f1={n['f1']:.3f} cons={n['hard_rule_consistency']:.3f} | "
            f"hybrid acc={h['accuracy']:.3f} f1={h['f1']:.3f} cons={h['hard_rule_consistency']:.3f} "
            f"override={h['override_rate']:.3f} conflict={h['conflict_rate']:.3f} | "
            f"symbolic acc={run.systems['symbolic']['accuracy']:.3f}"
        )


if __name__ == "__main__":
    main(sys.argv[1:])
