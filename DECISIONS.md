# ARCHITECTURAL DECISIONS RECORD (ADR)

## ADR-001: Authentic Neuro-Symbolic Separation over Pure LLM Chatbot
- **Context:** Many modern "agent" prototypes simply invoke general-purpose LLMs in a loop and label it neuro-symbolic.
- **Decision:** Implement genuine statistical machine learning (Scikit-Learn/LightGBM/PyTorch) for the Neural Agent, a deterministic Python forward-chaining engine for the Symbolic Agent, programmatic guards for the Validation Agent, and reserve LLMs purely for natural-language query normalization and narrative report rendering.
- **Rationale:** Preserves the core scientific validity of the original research synopsis and ensures deterministic reproducibility, explainability, and regulatory compliance.

## ADR-002: Modular Monolith Architecture
- **Context:** Evaluating whether to build distributed microservices with Kafka/gRPC or a unified modular monolith.
- **Decision:** Build a high-performance modular monolith using FastAPI (Python 3.10+) for the backend engine and Next.js / React (TypeScript) for the enterprise interface.
- **Rationale:** Eliminates network serialization latency between cooperating agents, simplifies local reproducibility for academic evaluation, and facilitates atomic transaction audit logging.

## ADR-003: Deterministic Rule Engine with Precedence Over Probabilities
- **Context:** How to combine neural predictions with legal or compliance constraints.
- **Decision:** Hard constraints (e.g., sanctioned destination, KYC freeze, impossible velocity) strictly override probabilistic neural predictions, logging a `SYMBOLIC_OVERRIDE` trace event.
- **Rationale:** In high-stakes financial domains, regulatory compliance is non-negotiable regardless of how low a neural model predicts risk.

## ADR-004: Calibrated Probabilities and SHAP for Neural Explainability
- **Context:** Raw softmax or decision-tree leaf outputs do not represent true empirical probabilities.
- **Decision:** Calibrate neural model outputs using Platt Scaling / Isotonic Regression and compute local feature attributions via TreeSHAP/LinearSHAP.
- **Rationale:** Provides scientifically defensible feature importance and confidence intervals rather than arbitrary pseudo-probabilities.

## ADR-005: Resolution of Misplaced Crime Safety Scope in Synopsis
- **Context:** Page 7 of the submitted synopsis contained text on "crime-route prediction and mobile safety".
- **Decision:** Exclude the mobile crime safety text and focus exclusively on high-stakes Financial Transaction Risk Analysis and Decision Support.
- **Rationale:** The safety text is an acknowledged artifact that directly contradicts the title, methodology, and evaluation criteria of the primary project.
