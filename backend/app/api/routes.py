"""REST API: domains, decisions, history, statistics and evaluation."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app import storage
from app.agents.coordinator_agent import coordinator
from app.core.domain_manager import domain_manager
from app.core.evaluation import evaluate_domain, load_results
from app.domains.base import DomainDefinition
from app.schemas import (
    DecisionRequest,
    DecisionResult,
    DecisionSummary,
    DomainDetail,
    DomainSummary,
    EvaluationRun,
    FeedbackRequest,
    StatsResponse,
)

router = APIRouter(prefix="/api")


def _domain_or_404(domain_id: str) -> DomainDefinition:
    try:
        return domain_manager.get(domain_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown domain '{domain_id}'") from exc


def _summary(d: DomainDefinition) -> DomainSummary:
    meta = domain_manager.metadata(d.id)
    return DomainSummary(
        id=d.id, name=d.name, title=d.title, tagline=d.tagline, description=d.description, icon=d.icon,
        task_type=d.task_type, classes=d.classes, feature_count=len(d.features), rule_count=len(d.rules),
        model_ready=domain_manager.model_ready(d.id), model_accuracy=meta.get("test_accuracy") if meta else None,
    )


# ------------------------------------------------------------------- domains
@router.get("/domains", response_model=list[DomainSummary], tags=["Domains"])
def list_domains() -> list[DomainSummary]:
    return [_summary(d) for d in domain_manager.list()]


@router.get("/domains/{domain_id}", response_model=DomainDetail, tags=["Domains"])
def get_domain(domain_id: str) -> DomainDetail:
    d = _domain_or_404(domain_id)
    return DomainDetail(
        **_summary(d).model_dump(), features=d.features, derived_features=d.derived_features,
        rules=d.rules, presets=d.presets, disclaimer=d.disclaimer,
    )


@router.get("/domains/{domain_id}/model", tags=["Domains"])
def get_model_info(domain_id: str) -> dict[str, Any]:
    _domain_or_404(domain_id)
    domain_manager.get_model(domain_id)
    meta = dict(domain_manager.metadata(domain_id) or {})
    meta.pop("stats", None)
    return meta


@router.post("/domains/{domain_id}/train", tags=["Domains"])
def retrain(domain_id: str) -> dict[str, Any]:
    _domain_or_404(domain_id)
    bundle = domain_manager.train(domain_id)
    run = evaluate_domain(domain_id)
    meta = {k: v for k, v in bundle.metadata.items() if k != "stats"}
    return {"model": meta, "evaluation": run.model_dump()}


# ----------------------------------------------------------------- decisions
@router.post("/decisions", response_model=DecisionResult, tags=["Decisions"])
def create_decision(req: DecisionRequest) -> DecisionResult:
    _domain_or_404(req.domain)
    result = coordinator.decide(req.domain, req.inputs)
    storage.save_decision(result, source="form")
    return result


@router.get("/decisions", response_model=list[DecisionSummary], tags=["Decisions"])
def list_decisions(domain: str | None = None, limit: int = Query(200, ge=1, le=1000)) -> list[DecisionSummary]:
    return [storage.summarize(r) for r in storage.list_decisions(domain, limit)]


@router.get("/decisions/{decision_id}", response_model=DecisionResult, tags=["Decisions"])
def get_decision(decision_id: str) -> DecisionResult:
    r = storage.get_decision(decision_id)
    if not r:
        raise HTTPException(status_code=404, detail="Decision not found")
    return r


@router.delete("/decisions/{decision_id}", tags=["Decisions"])
def delete_decision(decision_id: str) -> dict[str, bool]:
    if not storage.delete_decision(decision_id):
        raise HTTPException(status_code=404, detail="Decision not found")
    return {"deleted": True}


@router.delete("/decisions", tags=["Decisions"])
def clear_decisions() -> dict[str, int]:
    return {"deleted": storage.clear_decisions()}


@router.post("/decisions/{decision_id}/feedback", tags=["Decisions"])
def feedback(decision_id: str, req: FeedbackRequest) -> dict[str, bool]:
    if not storage.set_feedback(decision_id, req.rating, req.comment):
        raise HTTPException(status_code=404, detail="Decision not found")
    return {"saved": True}


@router.get("/stats", response_model=StatsResponse, tags=["Decisions"])
def stats() -> StatsResponse:
    items = storage.list_decisions(limit=5000)
    n = len(items) or 1
    by_domain: dict[str, int] = {d.id: 0 for d in domain_manager.list()}
    by_tone = {"success": 0, "warning": 0, "danger": 0}
    for r in items:
        by_domain[r.domain] = by_domain.get(r.domain, 0) + 1
        by_tone[r.final_decision.tone] += 1
    rated = [r.feedback_rating for r in items if r.feedback_rating]
    return StatsResponse(
        total_decisions=len(items),
        by_domain=by_domain,
        by_tone=by_tone,
        override_rate=round(sum(r.fusion.override_applied for r in items) / n, 4),
        conflict_rate=round(sum(r.fusion.conflict.detected for r in items) / n, 4),
        review_rate=round(sum(r.validation.requires_human_review for r in items) / n, 4),
        avg_confidence=round(sum(r.final_decision.confidence for r in items) / n, 4) if items else 0.0,
        avg_feedback=round(sum(rated) / len(rated), 2) if rated else None,
        feedback_count=len(rated),
        recent=[storage.summarize(r) for r in items[:8]],
    )


# ---------------------------------------------------------------- evaluation
@router.get("/evaluation", response_model=list[EvaluationRun], tags=["Evaluation"])
def get_evaluation() -> list[EvaluationRun]:
    runs = load_results()
    if not runs:
        runs = [evaluate_domain(d.id) for d in domain_manager.list()]
    return runs


@router.post("/evaluation/run", response_model=list[EvaluationRun], tags=["Evaluation"])
def run_evaluation(domain: str | None = None) -> list[EvaluationRun]:
    targets = [_domain_or_404(domain).id] if domain else [d.id for d in domain_manager.list()]
    return [evaluate_domain(t) for t in targets]


@router.get("/agents", tags=["Framework"])
def agents() -> list[dict[str, str]]:
    from app.agents.explanation_agent import ExplanationAgent
    from app.agents.neural_agent import NeuralAgent
    from app.agents.symbolic_agent import SymbolicAgent
    from app.agents.validation_agent import ValidationAgent

    return [
        {"id": "coordinator", "name": coordinator.name, "role": coordinator.role},
        {"id": "neural", "name": NeuralAgent.name, "role": NeuralAgent.role},
        {"id": "symbolic", "name": SymbolicAgent.name, "role": SymbolicAgent.role},
        {"id": "validation", "name": ValidationAgent.name, "role": ValidationAgent.role},
        {"id": "explanation", "name": ExplanationAgent.name, "role": ExplanationAgent.role},
    ]
