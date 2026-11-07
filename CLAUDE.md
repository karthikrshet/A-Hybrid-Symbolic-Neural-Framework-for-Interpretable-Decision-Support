# CLAUDE.MD - Instructions for Claude Code & Coding Agents

## Project Overview
- **Project:** A Hybrid Symbolic-Neural Framework for Interpretable Decision Support
- **Architecture:** Multi-domain, multi-agent neuro-symbolic decision-support platform (FastAPI + scikit-learn MLP + deterministic rule engine + Next.js)
- **Domains:** Healthcare, Finance, Cyber Security (fraud detection), IT Troubleshooting, Education. All share one common engine.
- **Entry points:** ChatGPT-style assistant (`/chat`), structured Domain Analyzer (`/analyze`), landing page (`/`)

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
- **Model Training & Evaluation (from `backend/`):**
  ```bash
  python ml/train_pipeline.py            # add --fresh to regenerate datasets
  python experiments/evaluate_baseline_vs_hybrid.py
  ```
- **Frontend Setup & Run:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Code Guidelines
- Python: strict type hints (3.10+), Pydantic V2 schemas, Ruff/Black style.
- TypeScript: strict typing (no `any`), functional React components, Tailwind CSS, white + blue (`brand-*`) palette, icons from `react-icons/lu`.
- Agent contracts live in `backend/app/schemas.py`; `frontend/lib/types.ts` mirrors them, so keep both in sync.
- Domains are configuration: `backend/app/domains/<id>/{config,rules,chat}.py`. Agents must never import a domain directly.
- Decisions & evidence: every decision object must link neural attributions, triggered/passed rules, fusion rationale, validation checks and the agent trace.
- Fusion weights are tuned on the training split only; never tune on the test split.
