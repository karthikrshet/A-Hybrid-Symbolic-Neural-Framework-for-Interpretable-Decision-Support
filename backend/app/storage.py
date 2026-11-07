"""SQLite persistence for decision history and chat sessions (stdlib sqlite3)."""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from app.config import DB_PATH
from app.schemas import DecisionResult, DecisionSummary

_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    domain TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'form',
    session_id TEXT,
    payload TEXT NOT NULL,
    feedback_rating INTEGER,
    feedback_comment TEXT
);
CREATE INDEX IF NOT EXISTS ix_decisions_domain ON decisions(domain);
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT '{}',
    pinned INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    feedback INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_messages_session ON chat_messages(session_id, created_at);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with connect() as c:
        c.executescript(SCHEMA)


# ----------------------------------------------------------------- decisions
def save_decision(result: DecisionResult, source: str = "form", session_id: str | None = None) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO decisions (id, timestamp, domain, source, session_id, payload) VALUES (?, ?, ?, ?, ?, ?)",
            (result.id, result.timestamp, result.domain, source, session_id, result.model_dump_json()),
        )


def _to_result(row: sqlite3.Row) -> DecisionResult:
    result = DecisionResult.model_validate_json(row["payload"])
    result.feedback_rating = row["feedback_rating"]
    result.feedback_comment = row["feedback_comment"]
    return result


def summarize(r: DecisionResult) -> DecisionSummary:
    return DecisionSummary(
        id=r.id, timestamp=r.timestamp, domain=r.domain, domain_name=r.domain_name,
        neural_label=r.neural_prediction.label, final_label=r.final_decision.label,
        final_tone=r.final_decision.tone, confidence=r.final_decision.confidence,
        triggered_rules=len(r.symbolic_reasoning.triggered_rules), override_applied=r.fusion.override_applied,
        conflict=r.fusion.conflict.detected, requires_review=r.validation.requires_human_review,
        feedback_rating=r.feedback_rating,
    )


def list_decisions(domain: str | None = None, limit: int = 200) -> list[DecisionResult]:
    sql = "SELECT * FROM decisions"
    args: list[Any] = []
    if domain:
        sql += " WHERE domain = ?"
        args.append(domain)
    sql += " ORDER BY timestamp DESC LIMIT ?"
    args.append(limit)
    with connect() as c:
        return [_to_result(r) for r in c.execute(sql, args).fetchall()]


def get_decision(decision_id: str) -> DecisionResult | None:
    with connect() as c:
        row = c.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    return _to_result(row) if row else None


def delete_decision(decision_id: str) -> bool:
    with connect() as c:
        return c.execute("DELETE FROM decisions WHERE id = ?", (decision_id,)).rowcount > 0


def clear_decisions() -> int:
    with connect() as c:
        return c.execute("DELETE FROM decisions").rowcount


def set_feedback(decision_id: str, rating: int, comment: str | None) -> bool:
    with connect() as c:
        cur = c.execute(
            "UPDATE decisions SET feedback_rating = ?, feedback_comment = ? WHERE id = ?",
            (rating, comment, decision_id),
        )
        return cur.rowcount > 0


# ---------------------------------------------------------------------- chat
def create_session(session_id: str, title: str = "New chat") -> dict[str, Any]:
    ts = now()
    with connect() as c:
        c.execute("INSERT INTO chat_sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)", (session_id, title, ts, ts))
    return {"id": session_id, "title": title, "created_at": ts, "updated_at": ts, "pinned": False, "message_count": 0}


def list_sessions() -> list[dict[str, Any]]:
    with connect() as c:
        rows = c.execute(
            """SELECT s.*, (SELECT COUNT(*) FROM chat_messages m WHERE m.session_id = s.id) AS message_count
               FROM chat_sessions s ORDER BY s.pinned DESC, s.updated_at DESC"""
        ).fetchall()
    return [
        {"id": r["id"], "title": r["title"], "created_at": r["created_at"], "updated_at": r["updated_at"],
         "pinned": bool(r["pinned"]), "message_count": r["message_count"]}
        for r in rows
    ]


def get_session(session_id: str) -> dict[str, Any] | None:
    with connect() as c:
        row = c.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        return None
    return {"id": row["id"], "title": row["title"], "created_at": row["created_at"], "updated_at": row["updated_at"],
            "pinned": bool(row["pinned"]), "state": json.loads(row["state"] or "{}")}


def update_session(session_id: str, *, title: str | None = None, state: dict[str, Any] | None = None, pinned: bool | None = None) -> None:
    sets, args = ["updated_at = ?"], [now()]
    if title is not None:
        sets.append("title = ?")
        args.append(title)
    if state is not None:
        sets.append("state = ?")
        args.append(json.dumps(state))
    if pinned is not None:
        sets.append("pinned = ?")
        args.append(int(pinned))
    args.append(session_id)
    with connect() as c:
        c.execute(f"UPDATE chat_sessions SET {', '.join(sets)} WHERE id = ?", args)


def delete_session(session_id: str) -> bool:
    with connect() as c:
        c.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        return c.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,)).rowcount > 0


def add_message(message: dict[str, Any]) -> None:
    payload = {k: v for k, v in message.items() if k not in ("id", "session_id", "role", "content", "created_at", "feedback")}
    with connect() as c:
        c.execute(
            "INSERT INTO chat_messages (id, session_id, role, content, payload, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (message["id"], message["session_id"], message["role"], message["content"], json.dumps(payload, default=str), message["created_at"]),
        )


def list_messages(session_id: str) -> list[dict[str, Any]]:
    with connect() as c:
        rows = c.execute("SELECT * FROM chat_messages WHERE session_id = ? ORDER BY created_at, rowid", (session_id,)).fetchall()
    out: list[dict[str, Any]] = []
    for r in rows:
        msg = {"id": r["id"], "session_id": r["session_id"], "role": r["role"], "content": r["content"],
               "created_at": r["created_at"], "feedback": r["feedback"]}
        msg.update(json.loads(r["payload"] or "{}"))
        out.append(msg)
    return out


def set_message_feedback(message_id: str, value: int | None) -> bool:
    with connect() as c:
        return c.execute("UPDATE chat_messages SET feedback = ? WHERE id = ?", (value, message_id)).rowcount > 0


def delete_messages_after(session_id: str, created_at: str) -> None:
    with connect() as c:
        c.execute("DELETE FROM chat_messages WHERE session_id = ? AND created_at >= ?", (session_id, created_at))
