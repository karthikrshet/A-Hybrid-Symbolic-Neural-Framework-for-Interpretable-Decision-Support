"""Conversational multi-agent assistant (ChatGPT-style interface).

The chat layer is itself neuro-symbolic:

* **Neural query understanding** - two small neural text classifiers
  (TF-IDF n-grams → MLP) recognise the *intent* of the message and the
  *domain* it belongs to.
* **Symbolic entity extraction** - per-domain lexicons and regular-expression
  rules pull structured parameters ("BP 145/95", "₹5 lakh", "8 seconds") out of
  free text.
* **Coordinator routing** - both signals are fused, the conversation memory is
  updated (slot filling / what-if follow-ups) and the task is handed to the
  multi-agent decision pipeline.  The reply contains the answer, reasoning,
  supporting evidence and confidence.
"""

from __future__ import annotations

import importlib
import json
import re
import uuid
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import FeatureUnion, Pipeline

from app.agents.coordinator_agent import coordinator
from app.core.domain_manager import domain_manager
from app.core.evaluation import load_results
from app.core.llm import MESSAGE_SCHEMA, PROVIDER_LABELS, LLMClient, LLMError, understanding_schema
from app.domains.base import DomainDefinition
from app.schemas import DecisionResult

# --------------------------------------------------------------------------- #
# Training utterances for the neural intent classifier
# --------------------------------------------------------------------------- #
INTENT_UTTERANCES: dict[str, list[str]] = {
    "greeting": [
        "hi", "hello", "hey", "hey there", "good morning", "good evening", "hello assistant", "hi there",
        "namaste", "yo", "greetings", "hello how are you", "hi how are you doing", "good afternoon",
    ],
    "thanks": [
        "thanks", "thank you", "thanks a lot", "great thanks", "awesome thank you", "perfect thanks",
        "that helps", "thank you so much", "ok thanks", "cool thanks", "nice, thank you", "appreciate it",
    ],
    "help": [
        "what can you do", "help", "how do i use this", "what domains do you support", "show me examples",
        "what can i ask", "list your capabilities", "what tasks can you handle", "give me some example questions",
        "how can you help me", "what are your features", "which problems can you solve", "guide me",
    ],
    "about": [
        "how does this system work", "explain your architecture", "what agents are there", "how do the agents work together",
        "what is neuro symbolic ai", "what is a hybrid symbolic neural framework", "how do you make decisions",
        "explain the coordinator agent", "what does the validation agent do", "how is the decision fused",
        "why should i trust your answer", "what is decision fusion", "how do you explain decisions",
        "what model do you use", "tell me about the neural network", "what is symbolic reasoning",
        "how is this different from chatgpt", "explain the multi agent pipeline",
    ],
    "rules": [
        "show the rules", "what rules do you use", "list the knowledge base", "what are the finance rules",
        "show healthcare rules", "which rules apply to loans", "show me the fraud detection rules",
        "what thresholds do you use", "list the it monitoring rules", "what are the academic rules",
        "show the if then rules", "what is the knowledge base for education", "display rule set",
    ],
    "evaluation": [
        "how accurate are you", "show the evaluation", "what is the accuracy", "compare hybrid vs neural",
        "show benchmark results", "what is the f1 score", "how does the hybrid compare to a neural network",
        "show precision and recall", "model performance metrics", "how consistent are the decisions",
        "evaluation results for finance", "is the hybrid better than neural only",
    ],
    "analyze": [
        "is this transaction suspicious", "check my loan eligibility", "assess health risk", "analyse my server",
        "my cpu is at 95 percent", "student has 60 percent attendance", "blood pressure 150/100 glucose 140",
        "income 50000 credit score 700 loan 5 lakh", "transfer of 90000 at 3 am", "is this patient at risk",
        "can i get a loan", "why is my api slow", "will this student pass", "evaluate this case",
        "what if credit score was 650", "what if attendance is 80", "change glucose to 120", "now with bmi 32",
        "predict the risk", "diagnose this service", "is this payment fraud", "analyze this student",
        "patient aged 60 with sugar 200", "memory 92 percent and error rate 25 percent",
        "salary 30k wants loan of 10 lakh", "attendance 70 assignment 40 mock 35",
        "make a decision for this applicant", "assess this transaction", "the server is down",
        "is my health okay", "am i eligible", "what about with 3 backlogs",
    ],
}

INTENT_KEYWORDS: dict[str, list[str]] = {
    "rules": ["rule", "rules", "knowledge base", "thresholds", "if-then", "if then", "rule set"],
    "evaluation": ["accuracy", "accurate", "benchmark", "f1", "precision", "recall", "evaluation", "metrics", "hybrid vs", "compare hybrid"],
    "about": ["architecture", "how does this system", "how do you work", "agents work", "neuro-symbolic", "neuro symbolic", "decision fusion"],
}

WHAT_IF = re.compile(r"\b(what if|instead|change|now with|now|update|set|increase|decrease|reduce|raise|make it|same but|with)\b", re.I)

USE_DEFAULTS = re.compile(r"\b(use (?:the )?(?:typical|default|average|normal) values?|go ahead|proceed anyway|continue anyway|just analy[sz]e|skip (?:it|that))\b", re.I)

UNDERSTAND_SYSTEM = (
    "You are the query-understanding module of a multi-agent decision-support system. "
    "Classify the user's message and extract structured parameters. Intents: analyze (assess/predict/check a case, "
    "including what-if changes), greeting, thanks, help (what can you do), about (how the system/agents work), "
    "rules (show the knowledge base), evaluation (accuracy/benchmarks), general (anything else). "
    "Pick the domain that the message is about, or 'none'. If domain_selected_by_user is set, use it. "
    "Extract ONLY parameters that the user explicitly states, using the exact parameter names from the catalogue; "
    "convert units (e.g. '5 lakh' -> 500000, '8 seconds' -> 8000 for millisecond fields) and give values as plain strings. "
    "For option parameters return one of the listed options exactly. Never invent values. "
    "Set wants_defaults to true only if the user asks to continue with typical/default values."
)
CLARIFY_SYSTEM = (
    "You are the Coordinator agent of an explainable decision-support assistant. Some required details are missing. "
    "Write ONE short, friendly follow-up question (max 2 sentences, markdown allowed) asking for the missing details, "
    "briefly saying why they matter. Do not give any assessment yet. In 'suggestions' give 2-3 short example replies "
    "the user could click, each stating a plausible value for a missing detail."
)
NARRATIVE_SYSTEM = (
    "You are the Explanation agent of a hybrid neuro-symbolic decision-support system. Using ONLY the evidence JSON, "
    "write a clear 2-4 sentence plain-language summary for a non-expert: state the final decision exactly as given "
    "(use the exact label), why (neural factors and triggered rules), and the most important next step. "
    "Never change the decision, numbers or rules, never add facts that are not in the evidence, and do not give "
    "medical, legal or financial guarantees. In 'suggestions' give 3 short follow-up questions the user might ask next "
    "(e.g. a what-if change of one stated value, or asking about a rule)."
)
GENERAL_SYSTEM = (
    "You are the assistant of 'NeuroSymbolic AI', a hybrid symbolic-neural multi-agent decision-support platform "
    "(Coordinator, Neural, Reasoning, Validation and Explanation agents) for healthcare risk, loan eligibility, "
    "transaction fraud, IT failure detection and student performance. Answer the user's question helpfully and "
    "concisely in markdown (max ~150 words). If it is unrelated to these topics, answer briefly and suggest how the "
    "platform could help. Do not provide a domain decision yourself - decisions come from the agents. "
    "In 'suggestions' give 3 short follow-up prompts the user could send."
)
NUDGE_SYSTEM = (
    "The user has not replied to the assistant for a while. Rewrite default_nudge as one warm, short reminder "
    "(max 2 sentences) that helps them continue. Keep the same intent. In 'suggestions' return up to 3 quick replies, "
    "preferring the given quick_replies."
)

_NUM = r"(\d[\d,]*(?:\.\d+)?)\s*(k\b|thousand|lakhs?|lacs?|l\b|crores?|cr\b|million|mn\b|%|percent|ms\b|milliseconds?|s\b|secs?\b|seconds?|mins?\b|minutes?)?"
NUM_RE = re.compile(_NUM, re.I)


_UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
_SCALES = {"hundred": 100, "thousand": 1_000, "lakh": 100_000, "lakhs": 100_000, "crore": 10_000_000}
_WORD_NUM = re.compile(r"\b(?:(?:" + "|".join([*_UNITS, *_TENS, *_SCALES, "and"]) + r")[\s-]*)+\b", re.I)


def words_to_numbers(text: str) -> str:
    """'two hundred' -> '200', 'fifty eight' -> '58' (used before symbolic extraction)."""
    def convert(m: re.Match[str]) -> str:
        words = [w for w in re.split(r"[\s-]+", m.group(0).lower()) if w and w != "and"]
        if not words or all(w in _SCALES for w in words):
            return m.group(0)
        total = current = 0
        for w in words:
            if w in _UNITS:
                current += _UNITS[w]
            elif w in _TENS:
                current += _TENS[w]
            elif w == "hundred":
                current = max(current, 1) * 100
            else:
                total += max(current, 1) * _SCALES[w]
                current = 0
        trailing = " " if m.group(0).endswith((" ", "-")) else ""
        return f"{total + current}{trailing}"
    return _WORD_NUM.sub(convert, text)


def _parse_number(raw: str, unit: str | None, feature_unit: str) -> float:
    value = float(raw.replace(",", ""))
    u = (unit or "").lower().strip()
    if u in ("k", "thousand"):
        value *= 1_000
    elif u.startswith("lakh") or u.startswith("lac") or u == "l":
        value *= 100_000
    elif u.startswith("crore") or u == "cr":
        value *= 10_000_000
    elif u in ("million", "mn"):
        value *= 1_000_000
    if feature_unit == "ms":
        if u in ("s", "sec", "secs", "second", "seconds"):
            value *= 1000
        elif u.startswith("min"):
            value *= 60_000
        elif not u and value < 60:  # "response time 8" → seconds
            value *= 1000
    return value


@dataclass
class Routing:
    intent: str
    intent_confidence: float
    domain: str | None
    domain_confidence: float
    domain_scores: dict[str, float]
    extracted: dict[str, float | str] = field(default_factory=dict)
    assumed: dict[str, float | str] = field(default_factory=dict)
    what_if: bool = False
    method: str = ""


class QueryUnderstanding:
    """Neural intent + domain classifiers fused with symbolic keyword evidence."""

    def __init__(self) -> None:
        self.lexicons: dict[str, ModuleType] = {}
        for d in domain_manager.list():
            try:
                self.lexicons[d.id] = importlib.import_module(f"app.domains.{d.id}.chat")
            except ModuleNotFoundError:
                continue
        self.intent_model = self._build(INTENT_UTTERANCES)
        self.domain_model = self._build(self._domain_utterances())

    @staticmethod
    def _build(data: dict[str, list[str]]) -> Pipeline:
        texts, labels = [], []
        for label, items in data.items():
            texts.extend(items)
            labels.extend([label] * len(items))
        features = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)),
        ])
        model = Pipeline([
            ("tfidf", features),
            ("mlp", MLPClassifier(hidden_layer_sizes=(64,), max_iter=800, random_state=7, alpha=1e-4)),
        ])
        model.fit(texts, labels)
        return model

    def _domain_utterances(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        templates = ["{k}", "check {k}", "my {k} is high", "analyse {k}", "is the {k} ok", "{k} problem", "question about {k}"]
        for did, lex in self.lexicons.items():
            items: list[str] = list(lex.EXAMPLES)
            for k in lex.KEYWORDS:
                items.extend(t.format(k=k) for t in templates)
            for aliases in lex.ALIASES.values():
                items.extend(f"{a} 50" for a in aliases[:3])
            out[did] = items
        return out

    # ------------------------------------------------------------- detection
    def detect_intent(self, text: str, has_entities: bool) -> tuple[str, float, str]:
        probs = self.intent_model.predict_proba([text])[0]
        classes = list(self.intent_model.classes_)
        scores = dict(zip(classes, probs.tolist()))
        low = text.lower()
        method = "neural"
        for intent, kws in INTENT_KEYWORDS.items():
            if any(k in low for k in kws):
                scores[intent] = scores.get(intent, 0) + 0.6
                method = "neural + symbolic keywords"
        if has_entities:
            scores["analyze"] = scores.get("analyze", 0) + 0.8
            method = "neural + extracted parameters"
        total = sum(scores.values())
        best = max(scores, key=lambda k: scores[k])
        return best, scores[best] / total, method

    def detect_domain(self, text: str) -> tuple[str | None, float, dict[str, float]]:
        did, conf, scores, _ = self.detect_domain_explicit(text)
        return did, conf, scores

    def detect_domain_explicit(self, text: str) -> tuple[str | None, float, dict[str, float], bool]:
        probs = self.domain_model.predict_proba([text])[0]
        classes = list(self.domain_model.classes_)
        neural = dict(zip(classes, probs.tolist()))
        low = f" {text.lower()} "
        keyword_hits: dict[str, int] = {}
        for did, lex in self.lexicons.items():
            d = domain_manager.get(did)
            names = {d.name.lower(), d.id.replace("_", " "), d.title.lower(), *d.id.split("_")}
            hits = sum(2 for nm in names if len(nm) > 3 and re.search(rf"(?<![a-z]){re.escape(nm)}(?![a-z])", low))
            hits += sum(1 for k in lex.KEYWORDS if re.search(rf"(?<![a-z]){re.escape(k)}(?![a-z])", low))
            hits += sum(1 for aliases in lex.ALIASES.values() for a in aliases if len(a) > 3 and re.search(rf"(?<![a-z]){re.escape(a)}(?![a-z])", low))
            keyword_hits[did] = hits
        total_hits = sum(keyword_hits.values())
        fused: dict[str, float] = {}
        for did in self.lexicons:
            sym = keyword_hits[did] / total_hits if total_hits else 0.0
            fused[did] = 0.45 * neural.get(did, 0.0) + 0.55 * sym if total_hits else neural.get(did, 0.0)
        best = max(fused, key=lambda k: fused[k])
        confident = fused[best] >= 0.40 or (total_hits and keyword_hits[best] >= 1)
        return (best if confident else None), round(fused[best], 4), {k: round(v, 4) for k, v in fused.items()}, bool(total_hits)

    # ------------------------------------------------------------ extraction
    def extract(self, domain: DomainDefinition, text: str) -> dict[str, float | str]:
        lex = self.lexicons.get(domain.id)
        if lex is None:
            return {}
        units = {f.name: f.unit for f in domain.features}
        found: dict[str, float | str] = {}
        used: list[tuple[int, int]] = []
        low = words_to_numbers(text.lower())

        def free(a: int, b: int) -> bool:
            return all(b <= s or a >= e for s, e in used)

        # 1. special patterns (BP 145/95, "5 years tenure", "2 AM", "no backlogs")
        for pattern, targets in getattr(lex, "PATTERNS", []):
            for m in re.finditer(pattern, low):
                if not free(m.start(), m.end()):
                    continue
                key = targets[0]
                if key == "loan_tenure_years":
                    found["loan_tenure_months"] = float(m.group(1)) * 12
                elif key in ("past_defaults_zero", "backlogs_zero"):
                    found[key.replace("_zero", "")] = 0.0
                elif key == "hour_ampm":
                    h = int(m.group(1)) % 12
                    found["hour_of_day"] = float(h + 12 if m.group(2) == "pm" else h)
                elif key == "hour_midnight":
                    found["hour_of_day"] = 0.0
                else:
                    for i, t in enumerate(targets, start=1):
                        found[t] = float(m.group(i))
                used.append((m.start(), m.end()))
                break

        # 2. "alias … number" (forward) - longest aliases first
        pairs = sorted(((f, a) for f, al in lex.ALIASES.items() for a in al), key=lambda p: -len(p[1]))
        for feat, alias in pairs:
            if feat in found:
                continue
            rx = re.compile(rf"(?<![a-z]){re.escape(alias)}(?![a-z])[^\d\n,;]{{0,28}}?{_NUM}", re.I)
            for m in rx.finditer(low):
                ns = m.start(1)
                if not free(ns, m.end()):
                    continue
                found[feat] = _parse_number(m.group(1), m.group(2), units.get(feat, ""))
                used.append((ns, m.end()))
                break

        # 3. "number … alias" (reverse), e.g. "65% attendance", "3 backlogs", "45-year-old"
        for feat, alias in pairs:
            if feat in found:
                continue
            rx = re.compile(rf"{_NUM}[\s\-]*(?:[a-z/]+[\s\-]+){{0,2}}?{re.escape(alias)}(?![a-z])", re.I)
            for m in rx.finditer(low):
                if not free(m.start(1), m.end(1)):
                    continue
                found[feat] = _parse_number(m.group(1), m.group(2), units.get(feat, ""))
                used.append((m.start(1), m.end(1)))
                break

        # 4. categorical options - longest phrase first so "former smoker" beats "smoker"
        for feat, options in getattr(lex, "OPTION_ALIASES", {}).items():
            phrases = sorted(((opt, p) for opt, ps in options.items() for p in ps), key=lambda x: -len(x[1]))
            for opt, phrase in phrases:
                if re.search(rf"(?<![a-z]){re.escape(phrase)}(?![a-z])", low):
                    found[feat] = opt
                    break

        # 5. clip to the feature's valid range
        spec = {f.name: f for f in domain.features}
        for k, v in list(found.items()):
            if k not in spec:
                found.pop(k)
                continue
            f = spec[k]
            if isinstance(v, float) and f.kind == "number":
                lo = f.min if f.min is not None else v
                hi = f.max if f.max is not None else v
                if (lo > 0 and v < lo / 2) or (hi > 0 and v > hi * 2):
                    found.pop(k)  # far outside the valid range -> almost certainly a mis-read, not a real value
                    continue
                found[k] = float(min(max(v, lo), hi))
        return found


def _md_rules(domain: DomainDefinition) -> str:
    lines = [f"### Knowledge base - {domain.name} ({len(domain.rules)} rules)", "",
             "| ID | Rule | Condition | Implies | Type |", "|---|---|---|---|---|"]
    from app.core.rule_engine import condition_text
    for r in domain.rules:
        lines.append(
            f"| {r.id} | {r.name} | {condition_text(r, domain.feature_labels).replace('IF ', '')} | "
            f"{domain.class_by_level(r.implies_level).label} | {'Mandatory' if r.severity == 'hard' else 'Advisory'} |"
        )
    lines += ["", "*Mandatory* rules can override the neural prediction; *advisory* rules shift the fused belief."]
    return "\n".join(lines)


class ChatEngine:
    def __init__(self) -> None:
        self.nlu = QueryUnderstanding()
        self._llm_note: str | None = None
        self._picker_note: str | None = None

    # ------------------------------------------------------------------ public
    def suggestions(self) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for d in domain_manager.list():
            lex = self.nlu.lexicons.get(d.id)
            if lex:
                out.append({"domain": d.id, "domain_name": d.name, "icon": d.icon, "prompt": lex.EXAMPLES[0]})
        return out

    def respond(
        self,
        text: str,
        state: dict[str, Any],
        structured: dict[str, Any] | None = None,
        forced_domain: str | None = None,
        llm: LLMClient | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], DecisionResult | None]:
        """Return (assistant message payload, new session state, decision or None).

        ``forced_domain`` comes from the domain picker in the UI (``None`` = automatic routing).
        ``llm`` is optional: when configured it assists understanding and writing; the agents
        still make every decision, and any LLM failure falls back to the offline engine.
        """
        self._llm_note = None
        self._picker_note = None
        if structured:
            return self._structured(structured, state, llm)

        active = state.get("domain")
        domain_id, d_conf, d_scores, explicit = self.nlu.detect_domain_explicit(text)
        picker_note: str | None = None
        if forced_domain and domain_id and domain_id != forced_domain and explicit and d_conf >= 0.6:
            forced_ex = self.nlu.extract(domain_manager.get(forced_domain), text)
            detected_ex = self.nlu.extract(domain_manager.get(domain_id), text)
            if len(detected_ex) > len(forced_ex):
                # the message clearly belongs to another domain - don't give a wrong-domain answer
                picker_note = (f"*Your message looks like a **{domain_manager.get(domain_id).name}** question, so I routed it there "
                               f"instead of the selected {domain_manager.get(forced_domain).name} domain.*")
                forced_domain = None
        self._picker_note = picker_note
        if forced_domain:
            domain_id, d_conf, explicit = forced_domain, 1.0, True
            if active != forced_domain:
                active = None  # switching domain clears remembered parameters

        # entities - try detected domain first, then the active one (follow-ups)
        extracted: dict[str, float | str] = {}
        target = domain_id or active
        if target:
            extracted = self.nlu.extract(domain_manager.get(target), text)
        if not forced_domain and active and active != target:
            ex_active = self.nlu.extract(domain_manager.get(active), text)
            if len(ex_active) > len(extracted):
                target, extracted = active, ex_active
        intent, i_conf, method = self.nlu.detect_intent(text, has_entities=bool(extracted))
        wants_defaults = bool(USE_DEFAULTS.search(text)) and bool(active)
        if wants_defaults:
            intent, target = "analyze", active

        # ---- optional LLM understanding (fills gaps, never overrides the domain picker)
        if llm is not None:
            u = self._llm_understand(llm, text, state, forced_domain)
            if u is not None:
                method = f"{method} + LLM ({PROVIDER_LABELS[llm.config.provider]})"
                if u["intent"] == "general" and not extracted:
                    intent = "general"
                elif u["intent"] != intent and i_conf < 0.75 and not extracted:
                    intent = u["intent"]
                if not forced_domain and u["domain"] != "none":
                    if target is None or (d_conf < 0.6 and not extracted):
                        target, d_conf = u["domain"], max(d_conf, 0.8)
                if target:
                    llm_params = self._coerce_params(domain_manager.get(target), u["parameters"])
                    added = {k: v for k, v in llm_params.items() if k not in extracted}
                    if added:
                        extracted = {**extracted, **added}
                        if intent in ("general", "help", "greeting"):
                            intent = "analyze"
                if u["wants_defaults"] and active:
                    wants_defaults, intent, target = True, "analyze", active

        what_if = bool(active and target == active and WHAT_IF.search(text) and extracted)
        if domain_id is None and target == active and active:
            d_conf = max(d_conf, 0.5)

        routing = Routing(
            intent=intent, intent_confidence=round(i_conf, 4), domain=target, domain_confidence=d_conf,
            domain_scores=d_scores, extracted=extracted, what_if=what_if,
            method=f"{method} · domain selected by user" if forced_domain else method,
        )

        if intent == "greeting":
            return self._msg("text", self._greeting(), routing, llm=llm), state, None
        if intent == "thanks":
            return self._msg("text", "You're welcome! Ask me another question, or try a *what-if* follow-up such as **\"what if the credit score was 650?\"**", routing, llm=llm), state, None
        if intent == "help":
            return self._msg("text", self._help(), routing, llm=llm, suggestions=[s["prompt"] for s in self.suggestions()]), state, None
        if intent == "about":
            return self._msg("text", self._about(), routing, llm=llm), state, None
        if intent in ("rules", "evaluation") and not (domain_id and explicit):
            routing.domain = None  # general request - don't show a misleading domain chip
        if intent == "rules":
            d = domain_manager.get(domain_id) if (domain_id and explicit) else None
            body = _md_rules(d) if d else "\n\n".join(_md_rules(x) for x in domain_manager.list())
            return self._msg("rules", body, routing, llm=llm), state, None
        if intent == "evaluation":
            return self._msg("evaluation", self._evaluation(domain_id if explicit else None), routing, llm=llm), state, None
        if intent == "general":
            body, sugg = self._general_answer(llm, text) if llm else (self._fallback_general(), [])
            return self._msg("text", body, routing, llm=llm, suggestions=sugg or [s["prompt"] for s in self.suggestions()][:3]), state, None

        # ---- analyze intent
        if not target:
            return self._msg(
                "text",
                "I can analyse cases in **Healthcare, Finance, Cyber Security (fraud), IT Troubleshooting and Education**. "
                "Which domain is your question about? Pick one from the **Domain** bar below, or describe the case with numbers, "
                "e.g. *\"income ₹60,000, credit score 720, loan ₹5 lakh\"*.",
                routing, llm=llm, suggestions=[s["prompt"] for s in self.suggestions()],
            ), state, None

        domain = domain_manager.get(target)
        slots: dict[str, float | str] = dict(state.get("slots", {})) if target == active else {}
        slots.update(extracted)
        new_state = {"domain": target, "slots": slots}
        lex = self.nlu.lexicons.get(target)
        key = list(getattr(lex, "KEY_FEATURES", [])) if lex else []
        have_key = [k for k in key if k in slots]

        if len(have_key) < min(2, len(key)) and not wants_defaults:
            missing = [k for k in key if k not in slots]
            inputs = self._complete(domain, slots)[0]
            text_missing = ", ".join(f"**{domain.feature_labels[m]}**" for m in missing)
            body = (
                f"I'll route this to the **{domain.name} - {domain.title}** agents. "
                f"To give a reliable answer I need a few more details: {text_missing}.\n\n"
                "Reply with the values in plain language, fill in the form below, or say **\"use typical values\"**."
            )
            quick = self._missing_examples(domain, missing) + ["Use typical values"]
            if llm is not None:
                written = self._llm_clarify(llm, domain, text, slots, missing)
                if written:
                    body = f"{written[0]}\n\n*You can also fill in the form below, or say \"use typical values\".*"
                    quick = (written[1][:3] or quick[:-1]) + ["Use typical values"]
            return self._msg("clarify", body, routing, llm=llm,
                             form={"domain": target, "inputs": inputs, "missing": missing, "provided": list(slots)},
                             suggestions=quick), new_state, None

        inputs, assumed = self._complete(domain, slots)
        routing.assumed = assumed
        result = coordinator.decide(target, inputs)
        return self._decision_message(domain, result, routing, inputs, slots, llm), new_state, result

    # ----------------------------------------------------------------- helpers
    def _decision_message(
        self, domain: DomainDefinition, result: DecisionResult, routing: Routing,
        inputs: dict[str, float | str], slots: dict[str, float | str], llm: LLMClient | None,
    ) -> dict[str, Any]:
        body = self._decision_text(domain, result, routing)
        suggestions = self._followups(domain, result)
        if llm is not None:
            narrative = self._llm_narrative(llm, domain, result, routing)
            if narrative:
                head, _, rest = body.partition("\n\n")  # keep the "## label" heading first
                body = f"{head}\n\n{narrative[0]}\n\n{rest}"
                suggestions = list(dict.fromkeys([*narrative[1][:3], *suggestions]))[:4]
        return self._msg("decision", body, routing, llm=llm, decision=result.model_dump(), accuracy=self._accuracy(domain.id),
                         form={"domain": domain.id, "inputs": inputs, "missing": [], "provided": list(slots)},
                         suggestions=suggestions)

    def _structured(self, structured: dict[str, Any], state: dict[str, Any], llm: LLMClient | None = None) -> tuple[dict[str, Any], dict[str, Any], DecisionResult]:
        domain = domain_manager.get(structured["domain"])
        slots = {k: v for k, v in structured.get("inputs", {}).items() if v is not None and v != ""}
        inputs, assumed = self._complete(domain, slots)
        routing = Routing(intent="analyze", intent_confidence=1.0, domain=domain.id, domain_confidence=1.0,
                          domain_scores={domain.id: 1.0}, extracted=slots, assumed=assumed, method="structured form")
        result = coordinator.decide(domain.id, inputs)
        return self._decision_message(domain, result, routing, inputs, slots, llm), {"domain": domain.id, "slots": slots}, result

    # ------------------------------------------------------------- follow-ups
    def nudge(self, last: dict[str, Any] | None, llm: LLMClient | None = None) -> dict[str, Any]:
        """Gentle reminder when the user has not replied to the assistant's last message."""
        routing = Routing(intent="nudge", intent_confidence=1.0, domain=(last or {}).get("routing", {}).get("domain"),
                          domain_confidence=1.0, domain_scores={}, method="idle follow-up")
        kind = (last or {}).get("kind")
        form = (last or {}).get("form") or {}
        if kind == "clarify" and form.get("domain"):
            domain = domain_manager.get(form["domain"])
            missing = form.get("missing", [])
            names = ", ".join(domain.feature_labels.get(m, m) for m in missing) or "a few details"
            body = (f"Still there? I just need **{names}** to finish the {domain.name.lower()} analysis. "
                    "You can type the values, use the form above, or let me continue with typical values.")
            quick = self._missing_examples(domain, missing) + ["Use typical values"]
        elif kind == "decision":
            body = ("Would you like to explore this result further? You can change a value (*what-if*), "
                    "see the rules that were applied, or analyse a new case.")
            quick = list((last or {}).get("suggestions") or [])[:3] or ["Show the rules", "Analyse a new case"]
        else:
            body = "Is there anything I can help you analyse? Describe a patient, loan, transaction, server or student."
            quick = [s["prompt"] for s in self.suggestions()][:3]
        if llm is not None:
            try:
                data = llm.json(
                    NUDGE_SYSTEM,
                    json.dumps({"assistant_last_message": (last or {}).get("content", "")[:1500], "default_nudge": body, "quick_replies": quick}),
                    MESSAGE_SCHEMA,
                )
                if str(data.get("message", "")).strip():
                    body = str(data["message"]).strip()
                    quick = [str(x) for x in data.get("suggestions", [])][:3] or quick
                    if kind == "clarify" and "Use typical values" not in quick:
                        quick.append("Use typical values")
            except LLMError as exc:
                self._llm_note = str(exc)
        return self._msg("nudge", body, routing, llm=llm, suggestions=quick)

    @staticmethod
    def _missing_examples(domain: DomainDefinition, missing: list[str]) -> list[str]:
        spec = {f.name: f for f in domain.features}
        out: list[str] = []
        for m in missing[:2]:
            f = spec.get(m)
            if f is None:
                continue
            if f.kind == "select":
                out.append(f"{f.label} is {f.options[0] if f.options else f.default}")
                continue
            num = float(f.default)
            example = f"{num:,.0f}" if num.is_integer() else f"{num:g}"
            if f.unit == "₹":
                example = f"₹{example}"
            elif f.unit == "%":
                example = f"{example}%"
            elif f.unit and f.unit != "/100":
                example = f"{example} {f.unit}"
            out.append(f"{f.label} is {example}")
        return out

    # ------------------------------------------------------------- LLM helpers
    def _catalogue(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for d in domain_manager.list():
            out.append({
                "id": d.id, "title": d.title,
                "parameters": [
                    {"name": f.name, "label": f.label, "unit": f.unit, **({"options": f.options} if f.kind == "select" else {"min": f.min, "max": f.max})}
                    for f in d.features
                ],
            })
        return out

    def _llm_understand(self, llm: LLMClient, text: str, state: dict[str, Any], forced: str | None) -> dict[str, Any] | None:
        payload = {
            "message": text,
            "domain_selected_by_user": forced,
            "active_case": {"domain": state.get("domain"), "known_parameters": state.get("slots", {})},
            "domains": self._catalogue() if not forced else [c for c in self._catalogue() if c["id"] == forced],
        }
        try:
            data = llm.json(UNDERSTAND_SYSTEM, json.dumps(payload, default=str), understanding_schema([d.id for d in domain_manager.list()]))
        except LLMError as exc:
            self._llm_note = str(exc)
            return None
        valid = {d.id for d in domain_manager.list()}
        intents = {"analyze", "greeting", "thanks", "help", "about", "rules", "evaluation", "general"}
        return {
            "intent": data.get("intent") if data.get("intent") in intents else "analyze",
            "domain": data.get("domain") if data.get("domain") in valid else "none",
            "parameters": [p for p in data.get("parameters", []) if isinstance(p, dict)],
            "wants_defaults": bool(data.get("wants_defaults", False)),
        }

    @staticmethod
    def _coerce_params(domain: DomainDefinition, params: list[dict[str, Any]]) -> dict[str, float | str]:
        """Validate LLM-proposed parameters against the domain schema (symbolic guard-rail)."""
        spec = {f.name: f for f in domain.features}
        out: dict[str, float | str] = {}
        for p in params:
            f = spec.get(str(p.get("name", "")))
            if f is None:
                continue
            raw = str(p.get("value", "")).strip()
            if f.kind == "select":
                match = next((o for o in f.options if o.lower() == raw.lower()), None)
                if match:
                    out[f.name] = match
                continue
            m = NUM_RE.search(raw)
            if not m:
                continue
            v = _parse_number(m.group(1), m.group(2), f.unit)
            if f.min is not None:
                v = max(v, f.min)
            if f.max is not None:
                v = min(v, f.max)
            out[f.name] = float(v)
        return out

    def _llm_clarify(self, llm: LLMClient, domain: DomainDefinition, text: str, slots: dict[str, float | str], missing: list[str]) -> tuple[str, list[str]] | None:
        payload = {
            "user_message": text, "domain": domain.title, "already_known": slots,
            "missing": [{"name": m, "label": domain.feature_labels[m]} for m in missing],
        }
        try:
            data = llm.json(CLARIFY_SYSTEM, json.dumps(payload, default=str), MESSAGE_SCHEMA)
        except LLMError as exc:
            self._llm_note = str(exc)
            return None
        msg = str(data.get("message", "")).strip()
        return (msg, [str(x) for x in data.get("suggestions", [])]) if msg else None

    def _llm_narrative(self, llm: LLMClient, domain: DomainDefinition, r: DecisionResult, routing: Routing) -> tuple[str, list[str]] | None:
        evidence = {
            "domain": domain.title,
            "final_decision": {"label": r.final_decision.label, "confidence": r.final_decision.confidence},
            "neural_agent": {"label": r.neural_prediction.label, "confidence": r.neural_prediction.confidence,
                             "top_factors": [{"feature": a.label, "value": a.value, "effect": a.contribution} for a in r.neural_prediction.attributions[:4]]},
            "reasoning_agent": {"triggered_rules": [{"id": t.id, "name": t.name, "mandatory": t.severity == "hard", "message": t.description} for t in r.symbolic_reasoning.triggered_rules],
                                "rules_passed": len(r.symbolic_reasoning.passed_rules)},
            "coordinator": {"strategy": r.fusion.strategy, "override": r.fusion.override_applied, "conflict": r.fusion.conflict.description if r.fusion.conflict.detected else None},
            "validation_agent": {"human_review": r.validation.requires_human_review, "consistent_with_rules": r.validation.consistency_ok},
            "recommendations": r.recommendations[:4],
            "assumed_values": routing.assumed,
            "disclaimer": domain.disclaimer,
        }
        try:
            data = llm.json(NARRATIVE_SYSTEM, json.dumps(evidence, default=str), MESSAGE_SCHEMA)
        except LLMError as exc:
            self._llm_note = str(exc)
            return None
        msg = str(data.get("message", "")).strip()
        if not msg or r.final_decision.label.lower() not in msg.lower():
            return None  # grounding check: the narrative must state the agents' decision
        return msg, [str(x) for x in data.get("suggestions", [])]

    def _general_answer(self, llm: LLMClient, text: str) -> tuple[str, list[str]]:
        try:
            data = llm.json(GENERAL_SYSTEM, text, MESSAGE_SCHEMA)
            msg = str(data.get("message", "")).strip()
            if msg:
                return msg, [str(x) for x in data.get("suggestions", [])][:3]
        except LLMError as exc:
            self._llm_note = str(exc)
        return self._fallback_general(), []

    @staticmethod
    def _fallback_general() -> str:
        return ("I'm a decision-support assistant, so I focus on analysing cases in **healthcare, finance, cyber security, "
                "IT troubleshooting and education**. Describe a case with its numbers, or ask how the framework works. "
                "*(Connect an LLM in ⚙ settings for answers to general questions.)*")

    @staticmethod
    def _complete(domain: DomainDefinition, slots: dict[str, float | str]) -> tuple[dict[str, float | str], dict[str, float | str]]:
        """Fill parameters the user did not mention with typical values from the training data."""
        stats = domain_manager.get_model(domain.id).metadata["stats"]
        inputs: dict[str, float | str] = {}
        assumed: dict[str, float | str] = {}
        for f in domain.features:
            if f.name in slots:
                inputs[f.name] = slots[f.name]
                continue
            if f.kind == "number":
                v = stats.get("median", stats["mean"]).get(f.name, f.default)
                step = f.step or 1
                v = round(round(float(v) / step) * step, 2)
            else:
                v = stats["mode"].get(f.name, f.default)
            inputs[f.name] = v
            assumed[f.name] = v
        return inputs, assumed

    def _msg(self, kind: str, content: str, routing: Routing, llm: LLMClient | None = None, **extra: Any) -> dict[str, Any]:
        llm_info = None
        if llm is not None:
            llm_info = {"provider": llm.config.provider, "label": llm.config.label,
                        "used": self._llm_note is None, "error": self._llm_note}
        note = getattr(self, "_picker_note", None)
        if note and kind != "nudge":
            content = f"{note}\n\n{content}"
        return {
            "id": uuid.uuid4().hex,
            "role": "assistant",
            "kind": kind,
            "content": content,
            "picker_overridden": bool(note),
            "routing": {
                "intent": routing.intent, "intent_confidence": routing.intent_confidence,
                "domain": routing.domain, "domain_confidence": routing.domain_confidence,
                "domain_scores": routing.domain_scores, "extracted": routing.extracted,
                "assumed": routing.assumed, "what_if": routing.what_if, "method": routing.method,
                "llm": llm_info,
            },
            "suggestions": extra.pop("suggestions", []),
            **extra,
        }

    @staticmethod
    def _fmt(v: float | str, unit: str = "") -> str:
        if isinstance(v, str):
            return v
        s = f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.2f}".rstrip("0").rstrip(".")
        if unit == "₹":
            return f"₹{s}"
        return f"{s}{unit if unit in ('%',) else (' ' + unit if unit and unit != '/100' else '')}"

    def _decision_text(self, domain: DomainDefinition, r: DecisionResult, routing: Routing) -> str:
        units = {f.name: f.unit for f in domain.features}
        n, s, fz, fd, v = r.neural_prediction, r.symbolic_reasoning, r.fusion, r.final_decision, r.validation
        lines: list[str] = []
        if routing.what_if:
            changed = ", ".join(f"{domain.feature_labels[k]} → {self._fmt(val, units.get(k, ''))}" for k, val in routing.extracted.items())
            lines.append(f"*What-if analysis* - updated {changed}.\n")
        lines.append(f"## {fd.label}")
        lines.append(f"**{domain.title}** · final confidence **{fd.confidence:.0%}**\n")
        lines.append(r.explanation.summary + "\n")
        lines.append("**How the agents reached this conclusion**")
        lines.append(f"1. **Neural Agent** - predicted *{n.label}* ({n.confidence:.0%}).")
        if s.triggered_rules:
            names = ", ".join(f"{x.id} {x.name}" for x in s.triggered_rules[:4])
            lines.append(f"2. **Reasoning Agent** - {len(s.triggered_rules)} of {s.rules_evaluated} rules triggered: {names}.")
        else:
            lines.append(f"2. **Reasoning Agent** - all {s.rules_evaluated} rules passed.")
        lines.append(f"3. **Coordinator** - {fz.strategy.lower()}" + (f"; {fz.conflict.resolution}" if fz.conflict.detected else "; both channels agree."))
        lines.append(f"4. **Validation Agent** - " + ("consistent with all mandatory rules; " if v.consistency_ok else "inconsistency detected; ")
                     + ("**human review recommended**." if v.requires_human_review else "decision is reliable."))
        lines.append("5. **Explanation Agent** - evidence summarised below.\n")
        if r.recommendations:
            lines.append("**Recommended actions**")
            lines.extend(f"- {rec}" for rec in r.recommendations[:4])
            lines.append("")
        if routing.assumed:
            assumed = ", ".join(f"{domain.feature_labels[k]} = {self._fmt(val, units.get(k, ''))}" for k, val in list(routing.assumed.items())[:6])
            lines.append(f"> Values not mentioned were assumed typical: {assumed}. Tell me the real values to refine the result.\n")
        acc = self._accuracy(domain.id)
        if acc:
            lines.append(
                f"> **Measured accuracy ({domain.name}, {acc['test_samples']:,.0f} held-out test cases):** hybrid "
                f"{acc['hybrid_accuracy']:.1%} accuracy · F1 {acc['hybrid_f1']:.3f} · {acc['hybrid_consistency']:.0%} rule-consistent "
                f"(neural network alone: {acc['neural_accuracy']:.1%}).\n"
            )
        lines.append(f"*{domain.disclaimer}*")
        return "\n".join(lines)

    @staticmethod
    def _accuracy(domain_id: str) -> dict[str, float] | None:
        """Benchmark numbers for the domain, shown with every chat decision."""
        run = next((r for r in load_results() if r.domain == domain_id), None)
        if run is None:
            return None
        h, n = run.systems["hybrid"], run.systems["neural"]
        return {
            "test_samples": float(run.test_samples),
            "hybrid_accuracy": h["accuracy"], "hybrid_f1": h["f1"], "hybrid_consistency": h["hard_rule_consistency"],
            "neural_accuracy": n["accuracy"], "neural_f1": n["f1"],
        }

    def _followups(self, domain: DomainDefinition, r: DecisionResult) -> list[str]:
        out: list[str] = []
        for rule in r.symbolic_reasoning.triggered_rules[:3]:
            spec = next(x for x in domain.rules if x.id == rule.id)
            c = spec.conditions[0]
            # for a band rule (feature ≥ a AND feature < b) suggest leaving the band upwards
            upper = [x for x in spec.conditions if x.feature == c.feature and x.op in ("lt", "lte")]
            if c.op in ("gt", "gte") and upper:
                c = upper[0]
            if isinstance(c.value, (int, float)) and c.feature not in domain.derived_features:
                label = domain.feature_labels.get(c.feature, c.feature).lower()
                better = c.value * (0.95 if c.op in ("gt", "gte") else 1.1)
                better = round(better, 2) if better < 10 else round(better)
                out.append(f"What if {label} was {better:g}?")
        out = out[:2]
        out.append(f"Show the {domain.name.lower()} rules")
        out.append("How does the hybrid compare to a neural network?")
        return out[:4]

    def _greeting(self) -> str:
        return (
            "Hello! I'm the **NeuroSymbolic multi-agent assistant**. Instead of a single model, a team of specialised agents "
            "works on your question:\n\n"
            "- **Coordinator Agent** - understands the task and routes it\n"
            "- **Neural Agent** - predicts outcomes from learned patterns\n"
            "- **Reasoning Agent** - applies domain rules and constraints\n"
            "- **Validation Agent** - checks reliability and consistency\n"
            "- **Explanation Agent** - explains how the answer was reached\n\n"
            "Describe a case in plain language - a patient, a loan application, a transaction, a server or a student."
        )

    def _help(self) -> str:
        lines = ["Here's what I can do. Describe a case in your own words and include the numbers you know:\n"]
        for d in domain_manager.list():
            lex = self.nlu.lexicons.get(d.id)
            lines.append(f"**{d.name} - {d.title}**")
            if lex:
                lines.append(f"- *\"{lex.EXAMPLES[0]}\"*")
        lines += [
            "",
            "You can also ask:",
            "- **\"What if the glucose was 110?\"** - re-runs the last case with a changed value",
            "- **\"Show the finance rules\"** - lists the knowledge base",
            "- **\"How accurate is the hybrid model?\"** - benchmark results",
            "- **\"How does this system work?\"** - explains the architecture",
        ]
        return "\n".join(lines)

    def _about(self) -> str:
        return (
            "### How the hybrid neuro-symbolic framework works\n\n"
            "1. **Coordinator Agent** receives your message. A neural text classifier detects the *intent* and *domain*; "
            "symbolic extractors pull out the parameters.\n"
            "2. **Validation Agent** checks the inputs (ranges, missing values, unusual values).\n"
            "3. **Neural Agent** - a feed-forward neural network (64-32 ReLU, softmax) trained per domain - predicts the outcome "
            "with a confidence score and a feature attribution.\n"
            "4. **Reasoning Agent** evaluates the domain's IF-THEN knowledge base.\n"
            "5. **Coordinator** fuses both: `fused = w_n·P_neural + w_s·P_symbolic`, where the symbolic weight grows when the "
            "network is unsure; *mandatory* rules override the prediction when they're violated.\n"
            "6. **Validation Agent** verifies consistency with the rules and the confidence threshold, and flags cases for human review.\n"
            "7. **Explanation Agent** writes the justification from traceable evidence only - rules, attributions and the fusion policy.\n\n"
            "Unlike a general chatbot, every answer can be traced back to a rule or a measured feature contribution."
        )

    @staticmethod
    def _evaluation(domain_id: str | None) -> str:
        runs = load_results()
        if domain_id:
            runs = [r for r in runs if r.domain == domain_id] or runs
        if not runs:
            return "No benchmark has been run yet. Open the **Evaluation** page and click *Run benchmark*."
        lines = ["### Hybrid vs conventional neural network (held-out test sets)", "",
                 "| Domain | Neural acc | Hybrid acc | Neural F1 | Hybrid F1 | Rule consistency (NN → Hybrid) |",
                 "|---|---|---|---|---|---|"]
        for r in runs:
            n, h = r.systems["neural"], r.systems["hybrid"]
            lines.append(
                f"| {r.domain_name} | {n['accuracy']:.1%} | **{h['accuracy']:.1%}** | {n['f1']:.3f} | **{h['f1']:.3f}** | "
                f"{n['hard_rule_consistency']:.1%} → **{h['hard_rule_consistency']:.1%}** |"
            )
        avg = float(np.mean([r.improvement["f1"] for r in runs]))
        lines += ["", f"Average macro-F1 change: **{avg:+.3f}**. The hybrid never violates a mandatory rule, and every decision "
                      "carries explicit rule evidence in addition to feature attributions."]
        return "\n".join(lines)


_engine: ChatEngine | None = None


def get_engine() -> ChatEngine:
    global _engine
    if _engine is None:
        _engine = ChatEngine()
    return _engine
