# A Hybrid Symbolic-Neural Framework for Interpretable Decision Support

A **multi-domain, multi-agent neuro-symbolic decision-support platform**. Ask a question in plain language, the way you would in ChatGPT. Instead of one model answering, a team of specialised AI agents works on it together: one predicts, one applies rules, one validates and one explains. The reply is a decision with its **reasoning, supporting evidence and confidence**.

**Quick start:** see [How to run it (step by step)](#how-to-run-it-step-by-step).

---

## What it does

| Capability | How it is implemented |
|---|---|
| **ChatGPT-style AI assistant** | Conversational UI with saved sessions (rename, pin, delete, search), **automatic domain detection or a domain picker**, what-if follow-ups, follow-up questions for missing details ("use typical values" to continue), an idle reminder after 1 minute, suggested next questions, voice input, Markdown export, thumbs-up/down feedback |
| **Optional LLM integration** | Google Gemini, OpenAI or Anthropic Claude (chosen in the chat's ⚙ dialog or via environment variables). The LLM helps understand questions, writes grounded explanations and follow-up questions, and answers general questions. **The agents still make every decision**, and any LLM failure falls back to offline mode |
| **Multi-domain** | Healthcare · Finance · Cyber Security (fraud) · IT Troubleshooting · Education, all running on **one common engine** |
| **Neural agent** | Feed-forward neural network (MLP 64-32, ReLU, softmax) trained per domain, giving probabilities, confidence and a feature attribution |
| **Reasoning (symbolic) agent** | Deterministic IF-THEN rule engine; 47 rules across 5 knowledge bases (mandatory and advisory) |
| **Validation agent** | Input range checks, out-of-distribution detection, hard-rule consistency, confidence threshold, human-review flag |
| **Coordinator agent** | Routes the task, manages agent messages, **confidence-weighted fusion** plus **rule override**, conflict detection |
| **Explanation agent** | Human-readable justification built only from traceable evidence, plus counterfactuals and recommendations |
| **Evaluation** | Hybrid vs conventional neural network vs rules-only: accuracy, precision, recall, F1, rule consistency, interpretability |
| **History** | Every decision is stored with its full evidence trail; compare two decisions; rate explanations (1–5) |

## How a question is answered

```
User question ──► Coordinator Agent ──► Validation Agent (inputs)
  (chat/form)     • neural intent + domain classifier          │
                  • symbolic parameter extraction               ▼
                  • conversation memory (what-if)   ┌── Neural Agent ── prediction + confidence + attribution
                                                    └── Reasoning Agent ── triggered / passed rules
                                                                │
                         Coordinator: P = w_n·P_neural + w_s·P_symbolic, then hard-rule override
                                                                │
                         Validation Agent (consistency, confidence, review) ──► Explanation Agent
                                                                │
                         Final answer: decision + reasoning + evidence + confidence + recommendations
```

The chat layer is neuro-symbolic too. Two small neural text classifiers (TF-IDF → MLP) recognise the **intent** and the **domain**. Symbolic lexicons and regex rules extract parameters such as `BP 145/95`, `₹5 lakh` and `8 seconds`.

## LLM integration (optional)

Without an API key the assistant runs fully offline. To connect an LLM, either:

- open **AI Assistant → Connect LLM**, choose Gemini, OpenAI or Claude, paste a key and click *Test connection*. The key stays in your browser.
- or set environment variables before starting the backend: `LLM_PROVIDER` (`gemini` | `openai` | `anthropic`), the matching `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`, and optionally `LLM_MODEL`.

Default models: `gemini-2.5-flash`, `gpt-4o-mini`, `claude-opus-5-5`. For Claude, refusal fallbacks are enabled on supported models (`fallbacks: "default"`).

The LLM is used for four jobs: (1) intent, domain and parameter extraction, where its values are re-validated against the domain schema; (2) natural follow-up questions when details are missing; (3) a plain-language summary written **only from the agents' evidence**, which is dropped if it doesn't state the agents' decision; (4) answers to general questions. Every reply shows whether the LLM was used.

## Results (held-out test sets, 1,250 cases per domain)

| Domain | Test | NN acc. | Hybrid acc. | NN F1 | Hybrid F1 | NN rule consistency | Hybrid rule consistency | Rules-only acc. |
|---|---|---|---|---|---|---|---|---|
| Healthcare | 1250 | 83.8% | **84.6%** | 0.815 | **0.828** | 98.7% | **100.0%** | 61.3% |
| Finance | 1250 | 85.9% | **88.6%** | 0.772 | **0.819** | 97.6% | **100.0%** | 72.3% |
| Cyber Security | 1250 | 91.2% | **90.6%** | 0.794 | **0.789** | 100.0% | **100.0%** | 70.9% |
| IT Troubleshooting | 1250 | 88.8% | **89.2%** | 0.838 | **0.845** | 99.5% | **100.0%** | 74.6% |
| Education | 1250 | 90.2% | **90.1%** | 0.861 | **0.863** | 99.6% | **100.0%** | 60.1% |

The hybrid improves macro-F1 in 4 of 5 domains and **never violates a mandatory rule**. Every decision also carries explicit rule evidence on top of the neural attributions. Fusion weights were selected on the *training* split only. The test split is used only for these numbers.

## Project structure

```
backend/
├── app/
│   ├── agents/                 # coordinator, neural, symbolic, validation, explanation agents
│   ├── core/
│   │   ├── domain_manager.py   # discovers domains, loads/trains models
│   │   ├── rule_engine.py      # IF-THEN rule evaluation
│   │   ├── fusion_engine.py    # confidence-weighted fusion + rule override
│   │   ├── chat_engine.py      # conversational coordinator (intent, domain, slot filling)
│   │   └── evaluation.py       # hybrid vs neural benchmark
│   ├── domains/
│   │   ├── healthcare/         # config.py (schema, dataset) · rules.py (knowledge base) · chat.py (vocabulary)
│   │   ├── finance/
│   │   ├── fraud_detection/
│   │   ├── it_troubleshooting/
│   │   └── education/
│   ├── api/                    # REST + chat endpoints
│   ├── schemas.py              # Pydantic contracts shared by all agents
│   ├── storage.py              # SQLite: decisions, chat sessions, messages
│   └── main.py
├── ml/train_pipeline.py        # train all models + benchmark
├── experiments/                # evaluate_baseline_vs_hybrid.py + results/*.json
└── tests/
frontend/                       # Next.js 14 + TypeScript + Tailwind + React Icons
├── app/page.tsx                # landing page
└── app/(platform)/             # chat · dashboard · analyze · history · evaluation · knowledge-base · architecture
```

## How to run it (step by step)

You need **two terminals**: one for the backend (Python) and one for the frontend (website). Both must keep running while you use the app.

### Step 0: install the requirements (one time)

| Tool | Version | Check it with | Download |
|---|---|---|---|
| Python | 3.10 or newer | `python --version` | https://www.python.org/downloads/ (on Windows, tick **"Add Python to PATH"** during install) |
| Node.js | 18 or newer | `node --version` | https://nodejs.org/ (the LTS version) |
| Git | any | `git --version` | https://git-scm.com/downloads |

### Step 1: download the project

```bash
git clone https://github.com/karthikrshet/A-Hybrid-Symbolic-Neural-Framework-for-Interpretable-Decision-Support.git
```

```bash
cd A-Hybrid-Symbolic-Neural-Framework-for-Interpretable-Decision-Support
```

### Step 2: start the backend (terminal 1)

**Windows (Command Prompt or PowerShell):**

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

> **First start takes about 30–60 seconds.** The backend generates the five datasets and trains the five neural networks automatically. Wait until you see `Application startup complete`. Later starts are fast.
>
> If PowerShell blocks `venv\Scripts\activate`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt instead.

Check that it works: open http://localhost:8000/health. You should see `"status":"ok"`. The API documentation is at http://localhost:8000/docs.

### Step 3: start the frontend (terminal 2)

Open a **new** terminal in the project folder:

```bash
cd frontend
npm install
npm run dev
```

Wait for `Ready` / `Local: http://localhost:3000`.

### Step 4: open the app

Open **http://localhost:3000** in your browser.

| Page | URL | What it is |
|---|---|---|
| Landing page | http://localhost:3000 | Project overview |
| **AI Assistant (chat)** | http://localhost:3000/chat | Ask questions in plain language |
| Dashboard | http://localhost:3000/dashboard | Domains, statistics, recent decisions |
| Domain Analyzer | http://localhost:3000/analyze | Structured form for each domain |
| Decision History | http://localhost:3000/history | Past decisions, compare, rate explanations |
| Evaluation | http://localhost:3000/evaluation | Hybrid vs neural-network benchmark |
| Knowledge Base | http://localhost:3000/knowledge-base | Rules and model details |
| Architecture | http://localhost:3000/architecture | How the framework works |

The bottom-left of the app shows **"Agents online"** in green when the frontend can reach the backend.

### Step 5 (optional): connect an LLM

Everything works offline. To add an LLM, open the chat, click **Connect LLM** (top right), choose **Gemini**, **OpenAI** or **Claude**, paste your API key and click **Test connection**. See [LLM integration](#llm-integration-optional) for details.

### Every time after the first setup

Terminal 1:

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

On macOS / Linux, use `source venv/bin/activate` instead of `venv\Scripts\activate`.

Terminal 2:

```bash
cd frontend
npm run dev
```

### Useful commands (run inside `backend/` with the venv active)

Run the tests:

```bash
pytest -v
```

Retrain all models from fresh data and refresh the benchmark:

```bash
python ml/train_pipeline.py --fresh
```

Print the hybrid vs neural comparison table:

```bash
python experiments/evaluate_baseline_vs_hybrid.py
```

### Troubleshooting

| Problem | Fix |
|---|---|
| Chat says *"Cannot reach the backend"* / sidebar shows *Backend offline* | Terminal 1 must be running. On the first start, wait until training finishes (`Application startup complete`). |
| `python` is not recognised (Windows) | Reinstall Python with **"Add Python to PATH"** ticked, or use `py` instead of `python`. |
| `pip install` fails building packages | Upgrade pip first: `python -m pip install --upgrade pip`, then retry. Use Python 3.10–3.12. |
| Port 8000 or 3000 already in use | Stop the other program, or use another port: `uvicorn app.main:app --port 8001`, and start the frontend with `NEXT_PUBLIC_API_URL=http://localhost:8001` set in `frontend/.env.local`. |
| Reply says *"LLM unavailable — offline answer"* | The API key was rejected or the provider is unreachable. Open **Connect LLM** and click **Test connection** to see the exact error. |
| Start over with a clean history | Stop the backend and delete the `backend/data/` folder. |
| Retrain everything from scratch | Delete `backend/datasets/*.csv` and `backend/app/domains/*/model/`, then restart the backend. |

## Example chat prompts

- *Assess health risk: 45-year-old male, BP 145/95, glucose 160, BMI 29*, then *what if glucose was 110?*
- *Check loan eligibility: income ₹60,000/month, credit score 720, existing EMI ₹10,000, loan ₹5 lakh, salaried*
- *Is this transaction suspicious? ₹85,000 transfer at 2 AM from a new device, abroad, customer's average is ₹4,000*
- *My service has CPU 95%, memory 92%, API response time 8 seconds, error rate 25% and is unhealthy*
- *Student with 65% attendance, assignment 45/100, previous exam 50, mock test 40, studies 2 hours a day*
- *Show the finance rules* · *How accurate is the hybrid?* · *How does this system work?*

## Adding a new domain

1. Create `backend/app/domains/<name>/` with an empty `__init__.py`.
2. `config.py` defines a `DOMAIN = DomainDefinition(...)` with input schema, outcome classes, derived facts, dataset generator, presets and recommendations.
3. `rules.py` holds the IF-THEN knowledge base, built with `rule(...)` and `cond(...)`.
4. `chat.py` holds keywords, parameter aliases and example prompts for the assistant.
5. Restart the backend. The Domain Manager discovers the domain, trains its model and the UI shows it automatically.

## Data note

The datasets are **synthetic but structured on real guidance**: ACC/AHA blood-pressure bands, ADA glucose cut-offs, CIBIL bands and FOIR limits, AML/KYC red flags, SRE alert thresholds, and the 75% attendance / 40% pass-mark regulations. Ground truth comes from a noisy latent risk model plus domain policy, with 3% label noise. All outputs are decision support only. They are not medical, financial or legal advice.
