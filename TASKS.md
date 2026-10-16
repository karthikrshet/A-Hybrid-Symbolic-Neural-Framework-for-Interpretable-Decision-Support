# DEVELOPMENT ROADMAP & TASKS

## Phase 1: Architecture & Project Definition (CURRENT)
- [x] Extract and review original academic synopsis (`Synopsis report(Anjana) (1).docx`)
- [x] Detect scope contradictions (misplaced mobile safety crime-route section)
- [x] Author core architecture specification (`ARCHITECTURE.md`)
- [x] Establish architectural decisions record (`DECISIONS.md`)
- [x] Define Agent Responsibility Matrix & Decision Fusion Matrix
- [x] Set up persistent project context and memory (`PROJECT_CONTEXT.md`, `TASKS.md`, `AGENTS.md`, `CLAUDE.md`)

## Phase 2: Backend Core & Data Models
- [ ] Initialize Python backend with FastAPI, Pydantic V2, and SQLAlchemy
- [ ] Build database migrations and schema for users, sessions, decisions, and traces
- [ ] Implement JWT authentication, RBAC, and password hashing (bcrypt)
- [ ] Set up structured JSON logging with request correlation IDs and audit trail
- [ ] Author test suite for backend core endpoints

## Phase 3: Neural Intelligence Pipeline
- [ ] Acquire/generate authentic tabular financial transaction dataset with realistic class imbalance
- [ ] Implement reproducible data pipeline (cleaning, missing value handling, standard scaling, feature engineering)
- [ ] Train neural/gradient-boosted baseline (RandomForest, LightGBM, MLP)
- [ ] Implement probability calibration (Platt scaling / Isotonic regression)
- [ ] Integrate SHAP explainer for local feature attributions
- [ ] Persist model artifacts with version metadata and validation tests

## Phase 4: Symbolic Intelligence & Knowledge Base
- [ ] Design domain knowledge base for financial compliance, AML, and risk thresholds
- [ ] Implement deterministic forward-chaining inference engine
- [ ] Support hard constraints (overrides) and soft heuristic scoring rules
- [ ] Implement rule execution tracer returning exact triggered conditions
- [ ] Author unit tests for rule satisfaction, contradiction detection, and boundary cases

## Phase 5: Multi-Agent Orchestration & Contracts
- [ ] Define standardized Pydantic communication contracts (`AgentRequest`, `AgentResponse`, `ExecutionTrace`)
- [ ] Implement Coordinator Agent finite-state machine (`RECEIVED` -> `CLASSIFIED` -> `PLANNED` -> `EXECUTING` -> `FUSING` -> `VALIDATING` -> `EXPLAINING` -> `COMPLETED`)
- [ ] Implement task classifier distinguishing conversational queries from structured financial records
- [ ] Implement async dispatch, error handling, retry limits, and timeout protection

## Phase 6: Decision Fusion & Validation
- [ ] Implement Decision Fusion Policy Engine with explicit precedence logic
- [ ] Implement hard constraint overrides and conflict state detection
- [ ] Implement Validation Agent verifying schema conformance, evidence traceability, and score bounds
- [ ] Route borderline cases ($0.30 \le score \le 0.70$ or conflict) to `REQUIRES_HUMAN_REVIEW`

## Phase 7: Explainability Engine
- [ ] Construct human-readable explanations linking SHAP contributions and triggered rules
- [ ] Ensure zero hallucinated evidence (strictly grounded in agent outputs)
- [ ] Distinguish correlation vs regulatory rule causation in generated narratives

## Phase 8: Modern Enterprise Frontend
- [ ] Initialize Next.js 14+ (App Router) with TypeScript and Tailwind CSS
- [ ] Implement clean enterprise theme (white background, deep navy accents, neutral slate cards)
- [ ] Build AI Chat Workspace with real-time agent execution visualizer
- [ ] Build Decision Analysis Dashboard with confidence gauges, triggered rule tags, and SHAP waterfall chart
- [ ] Build Model Registry and Evaluation Benchmark comparison views
- [ ] Build Audit Trail viewer with full decision reconstruction

## Phase 9: Quality Assurance & Integration Testing
- [ ] End-to-end integration tests (FastAPI TestClient / Pytest)
- [ ] Stress and edge-case testing (missing features, extreme transaction values, rule conflicts)
- [ ] Security testing (SQL injection, XSS, unauthorized access, prompt injection resistance)

## Phase 10: Academic Research Benchmark
- [ ] Run benchmark comparing Neural-Only Baseline vs. Hybrid Neuro-Symbolic Multi-Agent System
- [ ] Compute metrics: Accuracy, Precision, Recall, F1-score, PR-AUC, Rule Consistency, Latency
- [ ] Generate comparative tables and visualizations for academic reporting

## Phase 11: Containerization & Deployment
- [ ] Author `Dockerfile` for backend and frontend
- [ ] Author `docker-compose.yml` with health check endpoints
- [ ] Provide comprehensive `README.md` and verification scripts
