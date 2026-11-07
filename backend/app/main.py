"""FastAPI entry point - Hybrid Symbolic-Neural Framework for Interpretable Decision Support."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.api import chat, routes
from app.config import CORS_ORIGIN_REGEX, PROJECT_NAME, VERSION
from app.core.chat_engine import get_engine
from app.core.domain_manager import domain_manager


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    storage.init_db()
    for d in domain_manager.list():  # loads saved models, trains any that are missing
        domain_manager.get_model(d.id)
    get_engine()  # warm up the neural query-understanding models
    yield


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="Multi-domain, multi-agent neuro-symbolic decision-support platform with explainable decisions.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)
app.include_router(chat.router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": VERSION,
        "domains": [d.id for d in domain_manager.list()],
        "models_ready": {d.id: domain_manager.model_ready(d.id) for d in domain_manager.list()},
    }
