"""Chat API - ChatGPT-style conversational access to the multi-agent framework."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app import storage
from app.core.chat_engine import get_engine
from app.core.domain_manager import domain_manager
from app.core.llm import DEFAULT_MODELS, PROVIDER_LABELS, LLMClient, LLMError, resolve_config

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(default="", max_length=4000)
    session_id: str | None = None
    structured: dict[str, Any] | None = None  # {"domain": "...", "inputs": {...}} from the inline form
    domain: str | None = None  # domain picker; None = automatic routing


class SessionPatch(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    pinned: bool | None = None


class MessageFeedback(BaseModel):
    value: int | None = Field(default=None, ge=-1, le=1)


def _title(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 48 else text[:45].rstrip() + "…"


@router.get("/suggestions")
def suggestions() -> list[dict[str, str]]:
    return get_engine().suggestions()


@router.get("/sessions")
def list_sessions() -> list[dict[str, Any]]:
    return storage.list_sessions()


@router.post("/sessions")
def new_session() -> dict[str, Any]:
    return storage.create_session(uuid.uuid4().hex)


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    s = storage.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return {**s, "messages": storage.list_messages(session_id)}


@router.patch("/sessions/{session_id}")
def patch_session(session_id: str, patch: SessionPatch) -> dict[str, bool]:
    if not storage.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    storage.update_session(session_id, title=patch.title, pinned=patch.pinned)
    return {"updated": True}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> dict[str, bool]:
    return {"deleted": storage.delete_session(session_id)}


@router.post("/messages/{message_id}/feedback")
def message_feedback(message_id: str, fb: MessageFeedback) -> dict[str, bool]:
    return {"saved": storage.set_message_feedback(message_id, fb.value)}


def _llm(request: Request) -> LLMClient | None:
    config = resolve_config(dict(request.headers))
    return LLMClient(config) if config else None


@router.get("/llm/status")
def llm_status(request: Request) -> dict[str, Any]:
    """Which LLM (if any) would be used - never returns the key."""
    config = resolve_config(dict(request.headers))
    return {
        "enabled": config is not None,
        "provider": config.provider if config else None,
        "label": config.label if config else None,
        "source": config.source if config else None,
        "providers": [{"id": k, "label": v, "default_model": DEFAULT_MODELS[k]} for k, v in PROVIDER_LABELS.items()],
    }


@router.post("/llm/test")
def llm_test(request: Request) -> dict[str, Any]:
    client = _llm(request)
    if client is None:
        raise HTTPException(status_code=400, detail="No LLM configured - choose a provider and enter an API key.")
    try:
        data = client.json(
            "You are a connectivity check. Reply with a JSON object.",
            "Return message='ok' and an empty suggestions list.",
            {"type": "object", "properties": {"message": {"type": "string"}, "suggestions": {"type": "array", "items": {"type": "string"}}},
             "required": ["message", "suggestions"], "additionalProperties": False},
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"ok": True, "label": client.config.label, "reply": str(data.get("message", ""))[:100]}


@router.post("/sessions/{session_id}/nudge")
def nudge(session_id: str, request: Request) -> dict[str, Any]:
    """Idle follow-up: called by the UI when the user has not replied for a while."""
    if not storage.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    messages = storage.list_messages(session_id)
    last = next((m for m in reversed(messages) if m["role"] == "assistant"), None)
    if last is None or last.get("kind") == "nudge":
        raise HTTPException(status_code=409, detail="Nothing to follow up on")
    payload = get_engine().nudge(last, _llm(request))
    msg = {**payload, "session_id": session_id, "created_at": storage.now()}
    storage.add_message(msg)
    storage.update_session(session_id)
    return {"message": {**msg, "feedback": None}}


@router.post("/message")
def send_message(req: ChatRequest, request: Request) -> dict[str, Any]:
    if not req.message.strip() and not req.structured:
        raise HTTPException(status_code=422, detail="Message is empty")
    if req.domain:
        try:
            domain_manager.get(req.domain)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown domain '{req.domain}'") from exc
    session = storage.get_session(req.session_id) if req.session_id else None
    if session is None:
        sid = req.session_id or uuid.uuid4().hex
        storage.create_session(sid)
        session = storage.get_session(sid)
    assert session is not None
    sid = session["id"]

    user_text = req.message.strip()
    if not user_text and req.structured:
        user_text = f"Analyse this {req.structured.get('domain', '').replace('_', ' ')} case using the form values."
    user_msg = {
        "id": uuid.uuid4().hex, "session_id": sid, "role": "user", "content": user_text,
        "created_at": storage.now(), "structured": req.structured,
    }
    storage.add_message(user_msg)

    payload, new_state, decision = get_engine().respond(req.message, session.get("state", {}), req.structured, req.domain, _llm(request))
    if decision is not None:
        storage.save_decision(decision, source="chat", session_id=sid)
        payload["decision_id"] = decision.id
    assistant = {**payload, "session_id": sid, "created_at": storage.now()}
    storage.add_message(assistant)

    title = _title(user_text) if session["title"] == "New chat" else None
    storage.update_session(sid, title=title, state=new_state)
    return {"session_id": sid, "title": title or session["title"], "user_message": user_msg, "message": {**assistant, "feedback": None}}
