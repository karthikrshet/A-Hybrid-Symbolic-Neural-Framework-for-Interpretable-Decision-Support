# API DOCUMENTATION

## Endpoints

### 1. Authentication
- `POST /api/v1/auth/register`: Register new user/analyst.
- `POST /api/v1/auth/login`: Authenticate and receive JWT access token.

### 2. Decision Analysis
- `POST /api/v1/decisions/analyze`: Ingest financial transaction record, trigger coordinator FSM, and return explainable decision.
- `GET /api/v1/decisions/history`: Query immutable audit history of past decisions.

### 3. Conversational Intelligence
- `POST /api/v1/chat/message`: Submit conversational questions or transactions for agent execution.

### 4. Symbolic Rules
- `GET /api/v1/rules/list`: Inspect all active symbolic compliance and risk rules.
- `POST /api/v1/rules/test`: Evaluate arbitrary facts against rule preconditions.

### 5. Audit & Integrity
- `GET /api/v1/audit/logs`: Retrieve chronological audit trail.
- `GET /api/v1/audit/verify`: Verify SHA-256 cryptographic chain integrity.
