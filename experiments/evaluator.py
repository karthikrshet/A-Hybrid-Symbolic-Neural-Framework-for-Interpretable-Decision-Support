import os
import json
import time
import asyncio
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    average_precision_score, roc_auc_score, confusion_matrix
)
from ml.datasets.generator import generate_financial_dataset
from ml.preprocessing.preprocessor import FinancialFeaturePreprocessor, FEATURE_COLUMNS
from ml.evaluation.metrics import compute_brier_score, compute_expected_calibration_error
from ai_engine.inference.model_manager import model_manager
from ai_engine.reasoning.rule_engine import rule_engine
from ai_engine.orchestration.coordinator import coordinator

async def run_benchmark_evaluation(n_test_samples: int = 200) -> dict:
    """
    Executes a comprehensive, 100% empirical evaluation on held-out test transactions,
    comparing Conventional Neural-Only Baseline vs. Proposed Hybrid Symbolic-Neural Multi-Agent Architecture.
    All metrics, rule consistencies, perturbations, and calibration scores are calculated dynamically.
    """
    print(f"=== INITIATING EVALUATION BENCHMARK ON {n_test_samples} HELD-OUT TRANSACTIONS ===")
    df = generate_financial_dataset(n_samples=n_test_samples, seed=1337)
    y_true = df["is_fraud"].values
    
    # 1. Evaluate Conventional Neural-Only Baseline
    print("Evaluating Conventional Neural-Only Baseline...")
    neural_preds = []
    neural_probs = []
    neural_latencies = []
    perturbed_neural_preds = []
    baseline_rule_consistent = 0
    
    for _, row in df.iterrows():
        data = row.to_dict()
        t0 = time.time()
        p, label, _ = model_manager.predict(data)
        neural_latencies.append((time.time() - t0) * 1000.0)
        neural_probs.append(p)
        pred_label = 1 if p >= 0.50 else 0
        neural_preds.append(pred_label)
        
        # Test 2% continuous feature perturbation for decision stability
        perturbed_data = data.copy()
        perturbed_data["transaction_amount"] = data["transaction_amount"] * 1.02
        perturbed_data["velocity_change_ratio"] = data["velocity_change_ratio"] * 1.02
        p_pert, _, _ = model_manager.predict(perturbed_data)
        perturbed_neural_preds.append(1 if p_pert >= 0.50 else 0)
        
        # Evaluate baseline rule consistency dynamically
        triggered_rules, has_override, rule_action = rule_engine.evaluate(data)
        if has_override:
            # Statutory compliance requires rejection (flag 1)
            if pred_label == 1:
                baseline_rule_consistent += 1
        else:
            # No hard override violated
            baseline_rule_consistent += 1
            
    neural_probs_arr = np.array(neural_probs)
    neural_preds_arr = np.array(neural_preds)
    perturbed_neural_preds_arr = np.array(perturbed_neural_preds)
    
    baseline_stability = float(np.mean(neural_preds_arr == perturbed_neural_preds_arr))
    baseline_rule_consistency = float(baseline_rule_consistent / len(df))
    
    baseline_metrics = {
        "accuracy": float(accuracy_score(y_true, neural_preds)),
        "precision": float(precision_score(y_true, neural_preds, zero_division=0)),
        "recall": float(recall_score(y_true, neural_preds, zero_division=0)),
        "f1_score": float(f1_score(y_true, neural_preds, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, neural_probs)),
        "roc_auc": float(roc_auc_score(y_true, neural_probs)),
        "brier_score": float(compute_brier_score(y_true, neural_probs_arr)),
        "expected_calibration_error": float(compute_expected_calibration_error(y_true, neural_probs_arr, n_bins=10)),
        "mean_latency_ms": float(np.mean(neural_latencies)),
        "rule_consistency_rate": baseline_rule_consistency,
        "decision_stability": baseline_stability,
        "interpretability_score": 0.0  # Neural-only baseline has 0 verifiable symbolic compliance linkage
    }
    
    # 2. Evaluate Proposed Hybrid Symbolic-Neural System
    print("Evaluating Proposed Hybrid Symbolic-Neural Multi-Agent System...")
    hybrid_preds = []
    hybrid_probs = []
    hybrid_latencies = []
    perturbed_hybrid_preds = []
    rule_overrides = 0
    human_reviews = 0
    hybrid_rule_consistent = 0
    interpretable_count = 0
    
    for _, row in df.iterrows():
        data = row.to_dict()
        res = await coordinator.execute_decision_pipeline(data)
        hybrid_latencies.append(res["latency_ms"])
        
        dec = res["final_decision"]
        is_pos = 1 if dec in ["REJECT", "FLAG_SUSPICIOUS"] else 0
        hybrid_preds.append(is_pos)
        hybrid_probs.append(res["neural_analysis"]["risk_probability"])
        
        # Test 2% perturbation on hybrid decision
        perturbed_data = data.copy()
        perturbed_data["transaction_amount"] = data["transaction_amount"] * 1.02
        perturbed_data["velocity_change_ratio"] = data["velocity_change_ratio"] * 1.02
        res_pert = await coordinator.execute_decision_pipeline(perturbed_data)
        pert_pos = 1 if res_pert["final_decision"] in ["REJECT", "FLAG_SUSPICIOUS"] else 0
        perturbed_hybrid_preds.append(pert_pos)
        
        if res["symbolic_analysis"].get("has_hard_override"):
            rule_overrides += 1
        if res["requires_human_review"]:
            human_reviews += 1
            
        # Verify strict invariant: if has_hard_override, dec MUST be REJECT
        if res["symbolic_analysis"].get("has_hard_override"):
            if dec == "REJECT":
                hybrid_rule_consistent += 1
        else:
            hybrid_rule_consistent += 1
            
        # Check verifiable evidence linking
        if len(res.get("explanation", {}).get("top_driving_features", [])) > 0 and len(res.get("execution_trace", [])) >= 5:
            interpretable_count += 1
            
    hybrid_probs_arr = np.array(hybrid_probs)
    hybrid_preds_arr = np.array(hybrid_preds)
    perturbed_hybrid_preds_arr = np.array(perturbed_hybrid_preds)
    
    hybrid_stability = float(np.mean(hybrid_preds_arr == perturbed_hybrid_preds_arr))
    hybrid_rule_consistency = float(hybrid_rule_consistent / len(df))
    hybrid_interpretability = float(interpretable_count / len(df))
    
    hybrid_metrics = {
        "accuracy": float(accuracy_score(y_true, hybrid_preds)),
        "precision": float(precision_score(y_true, hybrid_preds, zero_division=0)),
        "recall": float(recall_score(y_true, hybrid_preds, zero_division=0)),
        "f1_score": float(f1_score(y_true, hybrid_preds, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, hybrid_probs)),
        "roc_auc": float(roc_auc_score(y_true, hybrid_probs)),
        "brier_score": float(compute_brier_score(y_true, hybrid_probs_arr)),
        "expected_calibration_error": float(compute_expected_calibration_error(y_true, hybrid_probs_arr, n_bins=10)),
        "mean_latency_ms": float(np.mean(hybrid_latencies)),
        "rule_consistency_rate": hybrid_rule_consistency,
        "decision_stability": hybrid_stability,
        "interpretability_score": hybrid_interpretability,
        "rule_override_count": rule_overrides,
        "human_review_count": human_reviews
    }
    
    benchmark_report = {
        "experiment_name": "Conventional Neural Baseline vs. Proposed Hybrid Symbolic-Neural Multi-Agent Architecture",
        "sample_size": n_test_samples,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseline_neural_only": baseline_metrics,
        "hybrid_symbolic_neural": hybrid_metrics,
        "delta_improvements": {
            "accuracy_gain": float(hybrid_metrics["accuracy"] - baseline_metrics["accuracy"]),
            "precision_gain": float(hybrid_metrics["precision"] - baseline_metrics["precision"]),
            "recall_gain": float(hybrid_metrics["recall"] - baseline_metrics["recall"]),
            "f1_gain": float(hybrid_metrics["f1_score"] - baseline_metrics["f1_score"]),
            "pr_auc_gain": float(hybrid_metrics["pr_auc"] - baseline_metrics["pr_auc"]),
            "roc_auc_gain": float(hybrid_metrics["roc_auc"] - baseline_metrics["roc_auc"]),
            "rule_consistency_gain": float(hybrid_metrics["rule_consistency_rate"] - baseline_metrics["rule_consistency_rate"]),
            "stability_gain": float(hybrid_metrics["decision_stability"] - baseline_metrics["decision_stability"]),
            "interpretability_gain": float(hybrid_metrics["interpretability_score"] - baseline_metrics["interpretability_score"])
        }
    }
    
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "benchmark_results.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, indent=2)
        
    print(f"Benchmark results successfully persisted to {out_path}")
    return benchmark_report

# Alias for backwards compatibility
async def run_academic_benchmark(n_test_samples: int = 200):
    return await run_benchmark_evaluation(n_test_samples=n_test_samples)

if __name__ == "__main__":
    asyncio.run(run_benchmark_evaluation())
