# PROJECT CONTEXT

## Project Title
**A Hybrid Symbolic-Neural Framework for Interpretable Decision Support**

## Academic Affiliation & Attribution
- **Candidate:** Anjana Priya (USN: 3BR25MC009)
- **Institution:** Ballari Institute of Technology and Management (BITM), Hospet Road, Near Allipur, Ballari
- **Internal Guide:** Mrs. Subhashree D C (Assistant Professor) / Dr. S D N Hayath Ali (Associate Professor)
- **Course Code:** MPRJ384 (Semester: III)

---

## 1. Executive Summary & Vision
Modern machine learning models, especially deep neural networks and gradient-boosted ensembles, achieve high predictive accuracy on tabular and unstructured data but function as opaque black boxes. Conversely, classical symbolic Artificial Intelligence (expert systems, production rules, constraint logic) provides verifiable, deterministic, and auditable reasoning, but struggles with noisy, incomplete data and cannot learn patterns automatically.

This project delivers a **production-grade Neuro-Symbolic Multi-Agent Decision Support Platform**. It merges:
1. **Empirical Machine Learning:** A trained neural/probabilistic model generating calibrated risk scores with SHAP-based feature attributions.
2. **Deterministic Symbolic Logic:** A forward-chaining rule engine evaluating expert-defined financial regulations, velocity constraints, and compliance invariants.
3. **Multi-Agent Orchestration:** Specialized agents (Coordinator, Neural Analysis Agent, Symbolic Reasoning Agent, Validation Agent, Explanation Agent) communicating via typed Pydantic contracts.
4. **Decision Fusion Engine:** A formal fusion policy balancing neural probability, symbolic hard/soft constraints, conflict resolution, uncertainty quantification, and human-in-the-loop review routing.
5. **Auditable Explainability:** Human-readable explanations grounded strictly in observed agent outputs, feature importance, and triggered rule chains—never hallucinated chain-of-thought.

---

## 2. Core Academic Objectives
1. **Neural Pattern Recognition:** Process multi-feature financial transaction data, engineer temporal and behavioral features, train and calibrate predictive models (LightGBM, Random Forest, PyTorch MLP).
2. **Symbolic Rule Verification:** Maintain versioned domain knowledge bases with deterministic IF-THEN rules, evaluating hard constraints (e.g., sanctioned entity, velocity threshold, geographic impossibility).
3. **Multi-Agent Collaboration:** Coordinate execution through an explicit finite-state machine (FSM) controller tracking execution traces, latency, and agent health.
4. **Principled Decision Fusion:** Synthesize neural likelihood and symbolic constraints without naive averaging, enforcing policy overrides and uncertainty thresholds.
5. **Human-Centric Explainability:** Synthesize feature attributions (SHAP) and symbolic rule triggers into auditable decision reports for compliance officers.
6. **Empirical Evaluation:** Benchmark the hybrid system against a conventional neural-network-only baseline across Accuracy, Precision, Recall, F1-Score, PR-AUC, Rule Consistency, and Inference Latency.

---

## 3. Discrepancy & Scope Corrections
1. **Extraneous Mobile Safety Scope in Original Draft:**
   The submitted synopsis draft contained a misplaced paragraph on "AI-based mobile safety application and crime-route prediction". This was confirmed as an accidental artifact from another project. The scope is strictly focused on **Interpretable Decision Support in High-Stakes Financial Transactions**.
2. **Single Operational Domain:**
   While the architecture is domain-agnostic, the operational demonstrator is **Financial Transaction Risk & Fraud Decision Support** using verified, reproducible datasets.
3. **No LLM Substitution for ML:**
   The neural agent executes real machine learning models. LLMs are restricted strictly to natural language query parsing and narrative explanation synthesis.
