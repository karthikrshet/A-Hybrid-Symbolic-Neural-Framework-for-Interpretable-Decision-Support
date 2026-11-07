"""Coordinator Agent - manages agent communication and fuses their results.

It does not know what a blood-pressure value or a credit score means; it only
consumes the standardised agent outputs defined in :mod:`app.schemas`.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone

from app.agents.explanation_agent import ExplanationAgent
from app.agents.neural_agent import NeuralAgent
from app.agents.symbolic_agent import SymbolicAgent
from app.agents.validation_agent import ValidationAgent
from app.core.domain_manager import domain_manager
from app.core.fusion_engine import fuse
from app.schemas import AgentStep, DecisionResult


class CoordinatorAgent:
    name = "Coordinator Agent"
    role = "Routes the task, manages agent communication and performs decision fusion."

    def __init__(self) -> None:
        self.neural = NeuralAgent()
        self.symbolic = SymbolicAgent()
        self.validator = ValidationAgent()
        self.explainer = ExplanationAgent()

    def decide(self, domain_id: str, raw_inputs: Mapping[str, float | str]) -> DecisionResult:
        started = time.perf_counter()
        domain = domain_manager.get(domain_id)
        trace: list[AgentStep] = []

        def step(agent: str, role: str, action: str, summary: str, t0: float, warn: bool = False, sender: str = "Coordinator Agent", receiver: str | None = None) -> None:
            trace.append(AgentStep(
                order=len(trace) + 1, agent=agent, role=role, sender=sender, receiver=receiver or agent,
                action=action, summary=summary, duration_ms=round((time.perf_counter() - t0) * 1000, 2),
                status="warning" if warn else "completed",
            ))

        t = time.perf_counter()
        step(self.name, self.role, "Task routing",
             f"Domain '{domain.name}' selected - loaded input schema, {len(domain.rules)} rules and neural model.", t,
             sender="User", receiver=self.name)

        t = time.perf_counter()
        inputs, issues, ood = self.validator.validate_inputs(domain, raw_inputs)
        step(self.validator.name, self.validator.role, "Input validation",
             f"{len(domain.features)} inputs checked; {len(issues)} issue(s), {len(ood)} unusual value(s).", t, warn=bool(issues or ood))

        facts = domain.facts(inputs)

        t = time.perf_counter()
        neural = self.neural.run(domain, inputs)
        step(self.neural.name, self.neural.role, "Neural prediction",
             f"Predicted '{neural.label}' ({neural.confidence:.0%}); top driver: {neural.attributions[0].label if neural.attributions else '-'}.", t)

        t = time.perf_counter()
        symbolic = self.symbolic.run(domain, facts)
        step(self.symbolic.name, self.symbolic.role, "Rule-based reasoning",
             f"{symbolic.rules_evaluated} rules evaluated; {len(symbolic.triggered_rules)} triggered "
             f"({len(symbolic.violations)} mandatory) → at least '{symbolic.rule_label}'.", t, warn=bool(symbolic.violations))

        t = time.perf_counter()
        fusion, final = fuse(domain, neural, symbolic)
        step(self.name, self.role, "Decision fusion",
             f"{fusion.strategy}: final '{final.label}' ({final.confidence:.0%})."
             + (" Conflict resolved." if fusion.conflict.detected else ""), t, warn=fusion.conflict.detected)

        t = time.perf_counter()
        validation = self.validator.validate_decision(issues, ood, symbolic, fusion, final)
        step(self.validator.name, self.validator.role, "Decision verification",
             ("Consistent with all mandatory rules. " if validation.consistency_ok else "Inconsistency found. ")
             + ("Human review recommended." if validation.requires_human_review else "Reliable - no review required."),
             t, warn=validation.requires_human_review)

        t = time.perf_counter()
        explanation, recommendations = self.explainer.run(domain, facts, neural, symbolic, fusion, final, validation)
        step(self.explainer.name, self.explainer.role, "Explanation generation",
             f"Built explanation with {len(explanation.key_factors)} evidence items and {len(recommendations)} recommendations.", t)

        t = time.perf_counter()
        step(self.name, self.role, "Final response", f"Delivered '{final.label}' with reasoning, evidence and confidence.", t,
             receiver="User")

        return DecisionResult(
            id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
            domain=domain.id,
            domain_name=domain.name,
            inputs=inputs,
            derived={k: float(v) for k, v in facts.items() if k in domain.derived_features},
            neural_prediction=neural,
            symbolic_reasoning=symbolic,
            validation=validation,
            fusion=fusion,
            final_decision=final,
            explanation=explanation,
            recommendations=recommendations,
            agent_trace=trace,
            processing_ms=round((time.perf_counter() - started) * 1000, 2),
        )


coordinator = CoordinatorAgent()
