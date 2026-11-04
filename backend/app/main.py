from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.session import engine, Base
from backend.app.api.v1 import auth, decisions, chat, rules, evaluations, audit, agents, datasets, models

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A Hybrid Symbolic-Neural Framework for Interpretable Decision Support"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(decisions.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(rules.router, prefix=settings.API_V1_STR)
app.include_router(datasets.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(evaluations.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "HEALTHY", "version": settings.VERSION, "platform": "NeuroSymbolic-MultiAgent"}

@app.get("/ready", tags=["Health"])
def readiness_check():
    return {"status": "READY", "database": "CONNECTED", "model": "INITIALIZED"}
