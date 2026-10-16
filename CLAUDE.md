# CLAUDE.MD - Instructions for Claude Code & Coding Agents

## Project Overview
- **Project:** A Hybrid Symbolic-Neural Framework for Interpretable Decision Support
- **Architecture:** Neuro-Symbolic Multi-Agent Decision Support Platform (FastAPI + Next.js + Scikit-Learn + Deterministic Rule Engine)
- **Primary Domain Demonstrator:** Financial Transaction Risk & Fraud Decision Support

## Commands & Workflows
- **Backend Setup & Run:**
  ```bash
  cd backend
  python -m venv venv
  venv\Scripts\activate  # On Windows
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000
  ```
- **Backend Tests:**
  ```bash
  cd backend
  pytest -v
  ```
- **Model Training & Evaluation:**
  ```bash
  python ml/training/train_pipeline.py
  python experiments/evaluate_baseline_vs_hybrid.py
  ```
- **Frontend Setup & Run:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Code Guidelines
- Python: Strict type hinting with Python 3.10+, Pydantic V2 schemas, Ruff/Black formatting standards.
- TypeScript: Strict typing (no `any`), functional React components, Tailwind CSS with enterprise color palette (Navy/Slate/Clean White).
- Multi-Agent Contracts: Maintain strict contracts in `ai_engine/contracts/agent_schemas.py`.
- Decisions & Evidence: Always preserve evidence traceability; link SHAP attributions and triggered rules in every decision object.
