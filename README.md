# NeuroSymbolic AI: A Hybrid Symbolic-Neural Multi-Agent Decision Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![SHAP](https://img.shields.io/badge/SHAP-0.45+-red.svg)](https://shap.readthedocs.io/)
[![Tests](https://img.shields.io/badge/pytest-20%2F20%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade **Neuro-Symbolic Multi-Agent Decision Support Platform** combining genuine statistical machine learning models, deterministic forward-chaining symbolic rule engines, verifiable TreeSHAP explainability, and a modern conversational ChatGPT-style intelligence interface.

---

## Table of Contents
1. [Platform Overview & Vision](#platform-overview--vision)
2. [Multi-Agent Architecture & Coordination](#multi-agent-architecture--coordination)
3. [Machine Learning Pipeline](#machine-learning-pipeline)
4. [Symbolic Reasoning & Decision Fusion](#symbolic-reasoning--decision-fusion)
5. [Installation & Setup Guide](#installation--setup-guide)
6. [Running the Application](#running-the-application)
7. [Empirical Research Benchmarks](#empirical-research-benchmarks)
8. [Automated Test Suite](#automated-test-suite)
9. [REST API Reference](#rest-api-reference)
10. [Repository Structure](#repository-structure)
11. [License](#license)

---

## Platform Overview & Vision

Conventional machine learning models (Deep Neural Networks, Random Forests, Gradient Boosters) achieve high predictive performance on complex tabular and unstructured data, but operate as black boxes. They cannot guarantee strict regulatory compliance and are prone to uncalibrated margin errors in high-stakes environments.

Conversely, classical symbolic AI (expert systems, forward-chaining rule engines) provides 100% deterministic, auditable, and verifiable reasoning, but cannot learn patterns from noisy, multidimensional historical distributions.

**NeuroSymbolic AI** bridges this divide by deploying a coordinated team of **5 specialized autonomous AI agents**:
- **Zero Hallucination:** Regulatory violations trigger mathematical hard overrides (`SYMBOLIC_OVERRIDE`), guaranteeing policy compliance.
- **Calibrated Probabilities:** Neural likelihoods are scaled via Platt Sigmoid calibration (`CalibratedClassifierCV`) to ensure statistical validity.
- **Verifiable Auditability:** Decisions generate an immutable trace recording inputs, model version, active rule IDs, and local TreeSHAP attribution scores.
- **Conversational ChatGPT Interface:** An interactive chat workspace with collapsible agent collaboration traces, live scenario injection, and dynamic LLM integration.

---

## Multi-Agent Architecture & Coordination

The system coordinates agents through a formal **Finite State Machine (FSM)**:
`RECEIVED` &rarr; `CLASSIFIED` &rarr; `PLANNED` &rarr; `EXECUTING` &rarr; `FUSING` &rarr; `VALIDATING` &rarr; `EXPLAINING` &rarr; `COMPLETED`.

```
                    +--------------------------------+
                    |  User Interface / API Client   |
                    +--------------------------------+
                                   |
                                   v
                    +--------------------------------+
                    |       Coordinator Agent        |
                    |    (Task Routing & 7-State FSM)|
                    +--------------------------------+
                                   |
                  +----------------+----------------+
                  |                                 |
                  v                                 v
   +------------------------------+  +------------------------------+
   |       Neural AI Agent        |  |    Reasoning Agent (Symbolic)|
   | - Random Forest Classifier   |  | - Forward-Chaining Engine    |
   | - Platt Sigmoid Calibration  |  | - AML & Velocity Rules       |
   | - Feature Attribution (SHAP) |  | - Hard Constraint Overrides  |
   +------------------------------+  +------------------------------+
                  |                                 |
                  +----------------+----------------+
                                   |
                                   v
                    +--------------------------------+
                    |     Decision Fusion Engine     |
                    |  - Policy Precedence Matrix    |
                    |  - Uncertainty Band [0.3, 0.7] |
                    +--------------------------------+
                                   |
                                   v
                    +--------------------------------+
                    |        Validation Agent        |
                    |  - Integrity & Consistency     |
                    |  - Schema Contract Audit       |
                    +--------------------------------+
                                   |
                                   v
                    +--------------------------------+
                    |       Explanation Agent        |
                    |  - TreeSHAP Feature Waterfall  |
                    |  - Grounded Compliance Brief   |
                    +--------------------------------+
                                   |
                                   v
                    +--------------------------------+
                    |    Final Verified Decision     |
                    |   (ALLOW / REVIEW / REJECT)    |
                    +--------------------------------+
```

### The 5 Specialized Agents:
1. **Coordinator Agent:** Orchestrates communication, tracks execution time per step, and enforces state machine transitions.
2. **Neural AI Agent:** Preprocesses features, runs inference on the trained Scikit-Learn model artifact, and calculates local TreeSHAP values.
3. **Reasoning Agent:** Evaluates deterministic domain-specific facts against 8 versioned compliance rules without probabilistic ambiguity.
4. **Validation Agent:** Cross-verifies consistency between statistical predictions and symbolic invariants, detecting override conflicts.
5. **Explanation Agent:** Translates mathematical Shapley values and rule traces into clear, audit-compliant natural language briefs.

---

## Machine Learning Pipeline

### 1. Feature Space (14 Operational Dimensions)
The model trains on verified financial risk features:
- `transaction_amount` (float): Value in USD.
- `transaction_frequency_24h` (int): Number of transactions in trailing 24 hours.
- `velocity_change_ratio` (float): Ratio of current velocity to 30-day baseline.
- `location_distance_km` (float): Physical distance from user home coordinates.
- `hour_of_day` (int, 0-23): Hour of initiation.
- `is_weekend` (bool): Weekend indicator.
- `is_sanctioned_destination` (bool): OFAC/Statutory embargoed destination flag.
- `kyc_status` (str): `VERIFIED`, `INCOMPLETE`, or `PENDING`.
- `foreign_exchange_risk` (float, 0.0-1.0): Currency cross-border risk index.
- `ip_reputation_score` (float, 0.0-1.0): Network IP telemetry score.
- `device_trust_score` (float, 0.0-1.0): Hardware fingerprint integrity.
- `user_failed_attempts_1h` (int): Failed authentication count.
- `past_chargeback_count` (int): Historical disputes/chargebacks.
- `channel_type` (str): `MOBILE`, `WEB`, `ATM`, or `API`.

### 2. Model Training & Platt Calibration
- **Estimator:** Balanced Random Forest Classifier (100 estimators, max depth: 12).
- **Probability Calibration:** `CalibratedClassifierCV(estimator, method="sigmoid", cv="prefit")` via Platt scaling, mapping raw decision margins to true calibrated probabilities:
  $$P(y=1 | f(x)) = \frac{1}{1 + \exp(A \cdot f(x) + B)}$$
- **Held-Out Test Metrics:**
  - Accuracy: **82.7%**
  - Precision: **61.9%**
  - Recall: **48.8%**
  - F1-Score: **54.5%**
  - ROC-AUC: **83.8%**
  - PR-AUC: **60.5%**

### 3. Explainability via TreeSHAP
Local feature contributions are calculated dynamically via `shap.TreeExplainer`:
$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$
Attribution scores indicate exact positive or negative impact on the fraud probability.

### 4. Retraining the Model
To retrain and persist updated model artifacts:
```bash
# Via CLI:
python -c "from ml.training.train_model import train_and_persist_model; train_and_persist_model()"

# Via REST API:
curl -X POST http://127.0.0.1:8000/api/v1/models/retrain
```
Artifacts are automatically validated and written to [`ml/artifacts/`](ml/artifacts/).

---

## Symbolic Reasoning & Decision Fusion

### 1. Knowledge Base Rules
Defined in [`knowledge_base/rules/financial_risk_rules.json`](knowledge_base/rules/financial_risk_rules.json):
- `RULE-001: Sanctioned Jurisdiction Destination` &rarr; Action: `REJECT` (Priority: 100, Hard Override: `true`)
- `RULE-002: Excessive Velocity Ratio Spike` &rarr; Action: `FLAG_SUSPICIOUS` (Priority: 80, Hard Override: `false`)
- `RULE-003: Large Off-Hours Transfer Lacking KYC` &rarr; Action: `REQUIRES_HUMAN_REVIEW` (Priority: 75, Hard Override: `false`)
- `RULE-004: Compromised Device with Multiple Auth Failures` &rarr; Action: `REJECT` (Priority: 90, Hard Override: `true`)
- `RULE-005: High Chargeback History with High Amount` &rarr; Action: `REJECT` (Priority: 85, Hard Override: `true`)
- `RULE-006: High-Risk IP with Cross-Border Foreign Exchange` &rarr; Action: `FLAG_SUSPICIOUS` (Priority: 70, Hard Override: `false`)
- `RULE-007: Geographic Anomaly Distance Breach` &rarr; Action: `REQUIRES_HUMAN_REVIEW` (Priority: 65, Hard Override: `false`)
- `RULE-008: Trusted Domestic Low-Risk Transaction` &rarr; Action: `CLEAR` (Priority: 50, Hard Override: `false`)

### 2. Fusion Precedence Matrix
The Decision Fusion Policy balances neural probability $P(\text{Risk})$ against symbolic rule activations:
1. **Hard Override:** If any active rule has `has_hard_override = true`, its verdict overrides the neural score completely (e.g., Sanctioned Destination always yields `REJECT`).
2. **Consensus High-Risk:** If $P(\text{Risk}) \ge 0.70$ and soft risk rules fire &rarr; `REJECT`.
3. **Consensus Low-Risk:** If $P(\text{Risk}) < 0.30$ and clearance rules fire &rarr; `APPROVE`.
4. **Epistemic Uncertainty:** If $0.30 \le P(\text{Risk}) < 0.70$ or neural score contradicts soft rules &rarr; `REQUIRES_HUMAN_REVIEW`.

---

## Installation & Setup Guide

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** 18.0 or higher (with npm)
- **Git**

### Step 1: Clone the Repository
```bash
git clone https://github.com/karthikrshet/NeuroSymbolic-AI.git
cd NeuroSymbolic-AI
```

### Step 2: Backend Setup
```bash
# 1. Create and activate a Python virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux / macOS:
source venv/bin/activate

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Install project in editable mode
pip install -e .
```

### Step 3: Frontend Setup
```bash
# Navigate to frontend directory and install dependencies
cd frontend
npm install
cd ..
```

---

## Running the Application

### 1. Launch the Backend Server
From the project root with the virtual environment activated:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs (Swagger UI): **`http://127.0.0.1:8000/docs`**
- Alternative OpenAPI Spec (ReDoc): **`http://127.0.0.1:8000/redoc`**
- Health Check: **`http://127.0.0.1:8000/health`**

### 2. Launch the Frontend Application
In a separate terminal:
```bash
cd frontend
npm run dev
```
- AI Chat Workspace (ChatGPT UI): **`http://localhost:3000/chat`**
- Decision Studio & Overview: **`http://localhost:3000`**
- Benchmarks & Evaluations: **`http://localhost:3000/evaluations`**
- Live Agent Monitor: **`http://localhost:3000/agents`**
- Symbolic Rules Explorer: **`http://localhost:3000/rules`**
- Audit Trail: **`http://localhost:3000/audit`**

---

## Empirical Research Benchmarks

Run the evaluation suite comparing a **Neural-Only Baseline** against the **Hybrid Neuro-Symbolic Multi-Agent Framework** across 500 held-out test transactions:

```bash
python experiments/evaluator.py
```

### Benchmark Summary Results:
| Metric | Conventional Neural Baseline | Proposed Hybrid Framework | Delta Gain |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 82.2% | **82.4%** | +0.2% |
| **Precision** | 69.4% | **74.6%** | **+5.1%** |
| **Recall** | 42.7% | 37.6% | -5.1% (selective precision) |
| **F1-Score** | 52.9% | 50.0% | -2.9% |
| **PR-AUC** | 59.3% | **59.3%** | Baseline preserved |
| **Rule Consistency Rate** | 68.5% | **100.0%** | **+31.5% (Zero Violations)** |
| **Decision Stability** | 88.0% | **96.5%** | **+8.5%** |
| **Interpretability Index** | 42.0% | **94.0%** | **+52.0% (SHAP + Rules)** |
| **Mean Inference Latency**| 63.1 ms | 66.1 ms | +3.0 ms overhead |

---

## Automated Test Suite

The test suite covers API endpoints, FSM orchestration, ML training, symbolic rules, operators, circuit breakers, and probability calibration.

To run all unit and integration tests:
```bash
python -m pytest -v
```

**Results:**
```
tests/test_api.py::test_health PASSED
tests/test_api.py::test_decision_pipeline PASSED
tests/test_api.py::test_symbolic_override PASSED
tests/test_api.py::test_chat_endpoint PASSED
tests/test_calibration_metrics.py::test_platt_sigmoid_calibration PASSED
tests/test_circuit_breaker.py::test_circuit_breaker_flow PASSED
tests/test_coordinator_fsm.py::test_fsm_success_flow PASSED
tests/test_coordinator_fsm.py::test_fsm_invalid_state_transition PASSED
tests/test_coordinator_fsm.py::test_circuit_breaker_trip PASSED
tests/test_ml_pipeline.py::test_dataset_generator PASSED
tests/test_ml_pipeline.py::test_preprocessor PASSED
tests/test_ml_pipeline.py::test_model_inference PASSED
tests/test_ml_pipeline.py::test_shap_explainer PASSED
tests/test_operators.py::test_comparison_operators PASSED
tests/test_operators.py::test_membership_operators PASSED
tests/test_symbolic_engine.py::test_rule_engine_loading PASSED
tests/test_symbolic_engine.py::test_rule_evaluation PASSED
tests/test_symbolic_engine.py::test_hard_override PASSED
tests/test_validators.py::test_valid_input PASSED
tests/test_validators.py::test_invalid_amount PASSED

======================== 20 passed in 8.07s ========================
```

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health and platform version check |
| `POST` | `/api/v1/decisions/evaluate` | Execute full multi-agent decision pipeline on a transaction payload |
| `GET` | `/api/v1/decisions/history` | Retrieve historical decisions and execution traces |
| `POST` | `/api/v1/chat/message` | Conversational intelligence endpoint with dynamic LLM & agent routing |
| `GET` | `/api/v1/chat/conversations` | List conversation sessions for the chat workspace sidebar |
| `GET` | `/api/v1/agents` | Live agent registry, health status, and latency stats |
| `GET` | `/api/v1/rules` | List all 8 verified compliance and risk rules |
| `POST` | `/api/v1/rules/test` | Test facts against the symbolic rule engine directly |
| `GET` | `/api/v1/datasets/info` | Summary statistics of the active training dataset |
| `GET` | `/api/v1/datasets/sample` | Sample records from the transactions dataset |
| `GET` | `/api/v1/models/info` | Active ML model metadata, calibration metrics, and hyperparameters |
| `POST` | `/api/v1/models/retrain` | Retrain model artifact on synthetic distribution |
| `GET` | `/api/v1/evaluations/benchmark` | Retrieve latest comparative research benchmark metrics |
| `GET` | `/api/v1/audit/logs` | Query tamper-evident decision logs with SHA-256 hashes |
| `GET` | `/api/v1/audit/verify` | Verify cryptographic chain integrity of audit logs |

---

## Repository Structure

```
NeuroSymbolic-AI/
├── ai_engine/                         # Core Multi-Agent & Neuro-Symbolic Intelligence
│   ├── agents/                        # The 5 Specialized Autonomous Agents
│   │   ├── coordinator/               # Coordinator Agent (FSM Manager)
│   │   ├── neural/                    # Neural AI Agent (Model Inference)
│   │   ├── symbolic/                  # Symbolic Reasoning Agent (Rule Base)
│   │   ├── validation/                # Validation Agent (Conflict Checking)
│   │   └── explanation/               # Explanation Agent (SHAP & Synthesis)
│   ├── contracts/                     # Typed Pydantic V2 Communication Contracts
│   ├── explainability/                # TreeSHAP & Generative Explainer Services
│   ├── fusion/                        # Decision Fusion & Precedence Policy Engine
│   ├── inference/                     # Model Loader & Preprocessor Pipeline
│   ├── orchestration/                 # Coordinator FSM Implementation
│   └── reasoning/                     # Forward-Chaining Deterministic Rule Engine
├── backend/                           # FastAPI Application Service
│   └── app/
│       ├── api/v1/                    # Routers (chat, decisions, models, rules, etc.)
│       ├── core/                      # Configuration, JWT Security & Settings
│       ├── database/                  # SQLAlchemy Database Session & Models
│       ├── models/                    # Database ORM Entities
│       └── schemas/                   # API Request & Response Schemas
├── experiments/                       # Research Evaluation & Benchmarking
│   ├── benchmark_results.json         # Latest Benchmark Metrics
│   └── evaluator.py                   # Automated Baseline vs. Hybrid Evaluator
├── frontend/                          # Next.js 14 Enterprise Web Client
│   ├── app/
│   │   ├── chat/                      # Modern ChatGPT-Style Workspace (No Emojis)
│   │   ├── decision/                  # Interactive Analysis Studio
│   │   ├── evaluations/               # Benchmark Comparison Dashboard
│   │   ├── agents/                    # Live Agent Status & Topology
│   │   ├── models/                    # Model Registry & Metrics
│   │   ├── datasets/                  # Dataset Explorer
│   │   ├── rules/                     # Rule Base Inspector
│   │   ├── audit/                     # Cryptographic Audit Log
│   │   ├── history/                   # Decision History
│   │   └── settings/                  # System Configuration
│   └── components/                    # Reusable React UI Components (React Icons)
├── knowledge_base/                    # Verified Regulatory Knowledge Base
│   └── rules/financial_risk_rules.json # 8 AML, Velocity, and Sanction Rules
├── ml/                                # Machine Learning Artifacts & Training
│   ├── artifacts/                     # Persisted Trained Models (.joblib) & Metadata
│   ├── datasets/                      # Dataset Generator & Benchmark CSVs
│   ├── preprocessing/                 # Feature Transformers & Scalers
│   └── training/                      # Model Training & Platt Calibration Pipeline
├── tests/                             # Comprehensive Pytest Suite (20 Tests)
├── requirements.txt                   # Pinned Python Dependencies
├── setup.py                           # Package Installation Configuration
└── README.md                          # Comprehensive Documentation
```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
