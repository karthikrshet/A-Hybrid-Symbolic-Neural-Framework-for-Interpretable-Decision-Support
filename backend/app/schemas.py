"""Pydantic V2 contracts shared by every agent, the orchestrator and the API.

Every domain produces exactly the same output structure, which is what lets the
coordinator, the explanation agent and the frontend stay domain-independent.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Tone = Literal["success", "warning", "danger"]
Severity = Literal["hard", "soft"]
RuleStatus = Literal["TRIGGERED", "PASSED"]


# --------------------------------------------------------------------------- #
# Domain description (served to the frontend so forms are generated dynamically)
# --------------------------------------------------------------------------- #
class FeatureSpec(BaseModel):
    name: str
    label: str
    kind: Literal["number", "select"]
    description: str = ""
    unit: str = ""
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: float | str
    options: list[str] = Field(default_factory=list)
    group: str = "General"


class OutcomeClass(BaseModel):
    level: int
    key: str
    label: str
    tone: Tone
    description: str


class ConditionSpec(BaseModel):
    feature: str
    op: Literal["gt", "gte", "lt", "lte", "eq", "neq", "in"]
    value: float | str | list[str]


class RuleSpec(BaseModel):
    id: str
    name: str
    description: str
    category: str
    conditions: list[ConditionSpec]
    logic: Literal["all", "any"] = "all"
    implies_level: int
    severity: Severity
    recommendation: str
    pass_message: str = ""


class ScenarioPreset(BaseModel):
    id: str
    name: str
    description: str
    inputs: dict[str, float | str]


class DomainSummary(BaseModel):
    id: str
    name: str
    title: str
    tagline: str
    description: str
    icon: str
    task_type: str
    classes: list[OutcomeClass]
    feature_count: int
    rule_count: int
    model_ready: bool
    model_accuracy: float | None = None


class DomainDetail(DomainSummary):
    features: list[FeatureSpec]
    derived_features: dict[str, str]
    rules: list[RuleSpec]
    presets: list[ScenarioPreset]
    disclaimer: str


# --------------------------------------------------------------------------- #
# Agent outputs
# --------------------------------------------------------------------------- #
class FeatureAttribution(BaseModel):
    feature: str
    label: str
    value: float | str
    contribution: float  # signed change in probability of the predicted class


class NeuralPrediction(BaseModel):
    result: str
    label: str
    level: int
    confidence: float
    probabilities: dict[str, float]
    model: str
    attributions: list[FeatureAttribution]


class RuleEvaluation(BaseModel):
    id: str
    name: str
    description: str
    category: str
    status: RuleStatus
    severity: Severity
    implies_level: int
    implies_label: str
    condition_text: str
    observed: dict[str, float | str]
    recommendation: str
    message: str


class SymbolicReasoning(BaseModel):
    status: Literal["PASSED", "WARNINGS", "VIOLATIONS"]
    rule_level: int
    rule_label: str
    rules_evaluated: int
    triggered_rules: list[RuleEvaluation]
    passed_rules: list[RuleEvaluation]
    violations: list[str]
    distribution: dict[str, float]


class ValidationReport(BaseModel):
    input_valid: bool
    input_issues: list[str]
    out_of_distribution: list[str]
    consistency_ok: bool
    confidence_ok: bool
    requires_human_review: bool
    checks: list[str]


class ConflictInfo(BaseModel):
    detected: bool
    type: Literal["NONE", "NEURAL_UNDERESTIMATES", "NEURAL_OVERESTIMATES"]
    description: str
    resolution: str


class FusionResult(BaseModel):
    strategy: str
    neural_weight: float
    symbolic_weight: float
    fused_probabilities: dict[str, float]
    override_applied: bool
    override_rule_ids: list[str]
    conflict: ConflictInfo


class FinalDecision(BaseModel):
    result: str
    label: str
    level: int
    confidence: float
    tone: Tone


class Explanation(BaseModel):
    headline: str
    summary: str
    neural: str
    symbolic: str
    fusion: str
    key_factors: list[str]
    counterfactuals: list[str]
    disclaimer: str


class AgentStep(BaseModel):
    order: int
    agent: str
    role: str
    sender: str
    receiver: str
    action: str
    summary: str
    duration_ms: float
    status: Literal["completed", "warning"]


class DecisionRequest(BaseModel):
    domain: str
    inputs: dict[str, float | str]


class DecisionResult(BaseModel):
    id: str
    timestamp: str
    domain: str
    domain_name: str
    inputs: dict[str, float | str]
    derived: dict[str, float]
    neural_prediction: NeuralPrediction
    symbolic_reasoning: SymbolicReasoning
    validation: ValidationReport
    fusion: FusionResult
    final_decision: FinalDecision
    explanation: Explanation
    recommendations: list[str]
    agent_trace: list[AgentStep]
    processing_ms: float
    feedback_rating: int | None = None
    feedback_comment: str | None = None


class DecisionSummary(BaseModel):
    id: str
    timestamp: str
    domain: str
    domain_name: str
    neural_label: str
    final_label: str
    final_tone: Tone
    confidence: float
    triggered_rules: int
    override_applied: bool
    conflict: bool
    requires_review: bool
    feedback_rating: int | None = None


class FeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


class StatsResponse(BaseModel):
    total_decisions: int
    by_domain: dict[str, int]
    by_tone: dict[str, int]
    override_rate: float
    conflict_rate: float
    review_rate: float
    avg_confidence: float
    avg_feedback: float | None
    feedback_count: int
    recent: list[DecisionSummary]


class EvaluationRun(BaseModel):
    domain: str
    domain_name: str
    generated_at: str
    test_samples: int
    classes: list[str]
    systems: dict[str, dict[str, Any]]
    improvement: dict[str, float]
