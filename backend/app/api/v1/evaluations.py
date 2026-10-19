import os
import json
from fastapi import APIRouter

router = APIRouter(prefix="/evaluations", tags=["Evaluations & Benchmarks"])

@router.get("/latest")
def get_latest_benchmark():
    res_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../experiments/benchmark_results.json"))
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "status": "NOT_RUN",
        "message": "Benchmark not yet executed. Run 'python experiments/evaluator.py' to generate results."
    }
