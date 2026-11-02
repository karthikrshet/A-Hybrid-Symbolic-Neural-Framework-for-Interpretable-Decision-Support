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

---

## 4. Plain-Language Explanation & Multi-Agent Architecture

### In Simple Words:
This project aims to build an AI-powered chatbot similar to ChatGPT, but instead of depending on a single AI model, it uses multiple specialized AI models (agents), where each model is responsible for a specific task.

When a user asks a question or provides a problem, the system intelligently identifies the task and routes it to the appropriate AI model or agent. These agents work together to analyze the input, generate predictions, apply logical rules, verify the results, and provide a final response with a clear explanation.

For example:
- **Neural AI Agent:** Understands user queries and identifies patterns using machine learning.
- **Reasoning Agent:** Applies logical rules and domain-specific knowledge.
- **Validation Agent:** Checks whether the generated answer is correct, consistent and reliable.
- **Explanation Agent:** Explains how the system reached its conclusion.
- **Coordinator Agent:** Manages communication between all agents and combines their results.

### How the System Works:
1. **User Interface (AI Chatbot):** User enters a question or task.
2. **Coordinator Agent:** Understands the task and selects appropriate agents.
3. **Neural Agent:** Prediction and pattern recognition.
4. **Reasoning Agent:** Rules and logical decisions.
5. **Validation Agent:** Checks reliability and consistency.
6. **Explanation Agent:** Generates understandable explanations.
7. **Final AI Response:** Answer + reasoning + supporting evidence + confidence.

### What Makes This Project Different:
Unlike a normal chatbot that primarily generates responses using one model, your platform will work like a team of AI specialists.

For example, if someone asks whether a particular financial transaction is suspicious:
1. The neural model identifies suspicious patterns.
2. The reasoning agent checks predefined fraud-detection rules.
3. The validation agent checks the prediction against the available evidence.
4. The explanation agent describes why the transaction was flagged.
5. The coordinator delivers the final result.

**Ultimate Goal:** Build a unified AI chatbot platform where multiple specialized AI models collaborate like a team to solve different tasks and provide accurate, validated, transparent and explainable answers.

