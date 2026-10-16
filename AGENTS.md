# AGENTS.MD - Operational Guide for Coding Agents

## System Identity & Philosophy
This repository implements **A Hybrid Symbolic-Neural Framework for Interpretable Decision Support**.
It is a genuine neuro-symbolic multi-agent architecture combining:
1. Genuine statistical machine learning models (Scikit-Learn/LightGBM/PyTorch)
2. Deterministic forward-chaining symbolic rule engine
3. Multi-agent coordinator with explicit finite-state machine workflows
4. Formal decision fusion policy with hard constraint overrides
5. Verifiable evidence linking with SHAP feature attributions
6. Scientific benchmarking comparing Neural-Only baseline vs. Hybrid Neuro-Symbolic framework

## Strict Rules of Engagement
1. **Never substitute an LLM call for the machine learning model.** The Neural Analysis Agent MUST call a real trained model artifact (.joblib or .pt) with preprocessing pipelines.
2. **Never substitute an LLM call for the symbolic rule engine.** The Symbolic Reasoning Agent MUST execute deterministic IF-THEN rules over a structured fact base.
3. **Never fabricate metrics or test outputs.** All benchmarks, evaluation tables, and test reports must reflect genuine executions over real test splits.
4. **All Agent communication must be typed.** Use Pydantic V2 schemas defined under `ai_engine/contracts/`. Never pass untyped strings between agents.
5. **No uncalibrated probabilities.** Model scores must be calibrated or explicitly labelled as raw decision function margins.
6. **Preserve auditability.** Every decision must produce an immutable trace recording inputs, model version, rule version, triggered rules, SHAP values, and fusion rationale.
