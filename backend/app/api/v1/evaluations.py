import os
import json
from fastapi import APIRouter

router = APIRouter(prefix="/evaluations", tags=["Evaluations & Benchmarks"])

def get_benchmark_file_path() -> str:
    # 4 levels up: v1 -> api -> app -> backend -> project_root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../experiments/benchmark_results.json"))

@router.get("")
@router.get("/latest")
@router.get("/benchmark")
async def get_latest_benchmark():
    res_path = get_benchmark_file_path()
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Auto-run dynamic evaluation if not yet present
    from experiments.evaluator import run_benchmark_evaluation
    results = await run_benchmark_evaluation(n_test_samples=100)
    return results

@router.post("/run")
async def trigger_benchmark_run(n_samples: int = 150):
    from experiments.evaluator import run_benchmark_evaluation
    results = await run_benchmark_evaluation(n_test_samples=n_samples)
    return results
