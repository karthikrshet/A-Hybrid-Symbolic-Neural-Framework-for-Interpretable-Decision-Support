"""Optional LLM integration (Google Gemini, OpenAI, Anthropic Claude).

The LLM never makes the decision - the neural, symbolic, validation and fusion
agents do.  It is used by the Coordinator and Explanation layers only to:

* understand free-text questions (intent, domain, parameters) more robustly,
* write natural follow-up questions when information is missing,
* turn the agents' structured evidence into a friendly, grounded narrative,
* answer general questions about the framework.

Configuration comes from request headers (the chat UI's settings dialog) or,
as a fallback, environment variables:
    LLM_PROVIDER = gemini | openai | anthropic
    LLM_MODEL    = optional model override
    GEMINI_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY
Every call is wrapped so that any failure falls back to the offline engine.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

import anthropic
import httpx

Provider = Literal["gemini", "openai", "anthropic"]
PROVIDERS: tuple[Provider, ...] = ("gemini", "openai", "anthropic")

DEFAULT_MODELS: dict[Provider, str] = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-opus-5-5",
}
ENV_KEYS: dict[Provider, str] = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}
PROVIDER_LABELS: dict[Provider, str] = {"gemini": "Google Gemini", "openai": "OpenAI", "anthropic": "Anthropic Claude"}

# Claude models that accept the effort setting and server-side refusal fallbacks ("default" mode)
_CLAUDE_FALLBACK_MODELS = ("claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5")
_CLAUDE_EFFORT_PREFIXES = ("claude-fable", "claude-opus-5", "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
                           "claude-sonnet-5", "claude-sonnet-4-6", "claude-haiku-5")
TIMEOUT_S = 60.0


class LLMError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMConfig:
    provider: Provider
    model: str
    api_key: str
    source: Literal["request", "environment"]

    @property
    def label(self) -> str:
        return f"{PROVIDER_LABELS[self.provider]} · {self.model}"


def resolve_config(headers: Mapping[str, str] | None = None) -> LLMConfig | None:
    """Request headers (settings dialog) take precedence over environment variables."""
    h = {k.lower(): v for k, v in (headers or {}).items()}
    provider = (h.get("x-llm-provider") or "").strip().lower()
    key = (h.get("x-llm-key") or "").strip()
    model = (h.get("x-llm-model") or "").strip()
    if provider in PROVIDERS and key:
        p: Provider = provider  # type: ignore[assignment]
        return LLMConfig(p, model or DEFAULT_MODELS[p], key, "request")
    if provider == "off":
        return None

    env_provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if env_provider == "off":
        return None
    candidates: list[Provider] = [env_provider] if env_provider in PROVIDERS else list(PROVIDERS)  # type: ignore[list-item]
    for p in candidates:
        env_key = os.getenv(ENV_KEYS[p], "").strip()
        if env_key:
            return LLMConfig(p, os.getenv("LLM_MODEL", "").strip() or DEFAULT_MODELS[p], env_key, "environment")
    return None


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    # ---------------------------------------------------------------- public
    def json(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Return a JSON object that follows ``schema`` (guaranteed on Claude, prompted on the others)."""
        if self.config.provider == "anthropic":
            text = self._claude(system, user, schema)
        else:
            instructed = (
                f"{system}\n\nRespond ONLY with a JSON object matching this JSON Schema "
                f"(no markdown fences):\n{json.dumps(schema)}"
            )
            text = self._gemini(instructed, user) if self.config.provider == "gemini" else self._openai(instructed, user)
        try:
            data = json.loads(_strip_fences(text))
        except json.JSONDecodeError as exc:
            raise LLMError(f"{PROVIDER_LABELS[self.config.provider]} returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise LLMError("LLM returned a non-object JSON value")
        return data

    # ------------------------------------------------------------- providers
    def _claude(self, system: str, user: str, schema: dict[str, Any]) -> str:
        client = anthropic.Anthropic(api_key=self.config.api_key, timeout=TIMEOUT_S, max_retries=1)
        model = self.config.model
        output_config: dict[str, Any] = {"format": {"type": "json_schema", "schema": schema}}
        if model.startswith(_CLAUDE_EFFORT_PREFIXES):
            output_config["effort"] = "low"  # chat-style extraction/writing: fast and cheap
        params: dict[str, Any] = {
            "model": model,
            "max_tokens": 16000,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": output_config,
        }
        try:
            if model in _CLAUDE_FALLBACK_MODELS:
                # on a policy decline the API re-runs the request on a suitable fallback model
                response = client.beta.messages.create(
                    betas=["server-side-fallback-2026-07-01"], fallbacks="default", **params
                )
            else:
                response = client.messages.create(**params)
        except anthropic.AuthenticationError as exc:
            raise LLMError("Anthropic rejected the API key") from exc
        except anthropic.NotFoundError as exc:
            raise LLMError(f"Unknown Claude model '{model}'") from exc
        except anthropic.RateLimitError as exc:
            raise LLMError("Anthropic rate limit reached - try again shortly") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Anthropic API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError("Cannot reach the Anthropic API") from exc
        if response.stop_reason == "refusal":
            raise LLMError("Claude declined this request")
        text = next((b.text for b in response.content if b.type == "text"), None)
        if text is None:
            raise LLMError("Claude returned no text")
        return text

    def _gemini(self, system: str, user: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent"
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3},
        }
        data = self._post(url, body, {"x-goog-api-key": self.config.api_key})
        try:
            return str(data["candidates"][0]["content"]["parts"][0]["text"])
        except (KeyError, IndexError, TypeError) as exc:
            reason = data.get("promptFeedback", {}).get("blockReason") if isinstance(data, dict) else None
            raise LLMError(f"Gemini returned no text{f' ({reason})' if reason else ''}") from exc

    def _openai(self, system: str, user: str) -> str:
        body = {
            "model": self.config.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }
        data = self._post("https://api.openai.com/v1/chat/completions", body, {"Authorization": f"Bearer {self.config.api_key}"})
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError("OpenAI returned no text") from exc

    def _post(self, url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        name = PROVIDER_LABELS[self.config.provider]
        try:
            r = httpx.post(url, json=body, headers=headers, timeout=TIMEOUT_S)
        except httpx.HTTPError as exc:
            raise LLMError(f"Cannot reach the {name} API") from exc
        if r.status_code in (401, 403):
            raise LLMError(f"{name} rejected the API key")
        if r.status_code == 404:
            raise LLMError(f"Unknown {name} model '{self.config.model}'")
        if r.status_code == 429:
            raise LLMError(f"{name} rate limit / quota reached")
        if r.status_code >= 400:
            try:
                msg = r.json().get("error", {}).get("message", r.text[:200])
            except ValueError:
                msg = r.text[:200]
            raise LLMError(f"{name} error {r.status_code}: {msg}")
        result: dict[str, Any] = r.json()
        return result


def _strip_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return t.strip()


# --------------------------------------------------------------------------- #
# Schemas shared by every provider (strict-compatible: no free-form keys)
# --------------------------------------------------------------------------- #
def understanding_schema(domain_ids: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "intent": {"type": "string", "enum": ["analyze", "greeting", "thanks", "help", "about", "rules", "evaluation", "general"]},
            "domain": {"type": "string", "enum": [*domain_ids, "none"]},
            "parameters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "value": {"type": "string"}},
                    "required": ["name", "value"],
                    "additionalProperties": False,
                },
            },
            "wants_defaults": {"type": "boolean"},
        },
        "required": ["intent", "domain", "parameters", "wants_defaults"],
        "additionalProperties": False,
    }


MESSAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["message", "suggestions"],
    "additionalProperties": False,
}
