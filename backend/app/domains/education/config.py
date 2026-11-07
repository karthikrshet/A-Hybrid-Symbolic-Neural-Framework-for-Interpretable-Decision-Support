"""Education domain - student performance assessment."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.domains.base import DomainDefinition, finalize_labels
from app.domains.education.rules import RULES
from app.schemas import FeatureSpec, OutcomeClass, ScenarioPreset

FEATURES = [
    FeatureSpec(name="attendance", label="Attendance", kind="number", unit="%", min=0, max=100, step=1, default=65, group="Engagement"),
    FeatureSpec(name="study_hours", label="Study hours / day", kind="number", unit="hours", min=0, max=12, step=0.5, default=2, group="Engagement"),
    FeatureSpec(name="participation", label="Class participation", kind="select", options=["Low", "Medium", "High"], default="Medium", group="Engagement"),
    FeatureSpec(name="assignment_score", label="Assignment score", kind="number", unit="/100", min=0, max=100, step=1, default=45, group="Academics"),
    FeatureSpec(name="previous_exam_score", label="Previous exam score", kind="number", unit="/100", min=0, max=100, step=1, default=50, group="Academics"),
    FeatureSpec(name="mock_test_score", label="Mock test score", kind="number", unit="/100", min=0, max=100, step=1, default=40, group="Academics"),
    FeatureSpec(name="backlogs", label="Pending backlogs", kind="number", unit="", min=0, max=10, step=1, default=0, group="Academics"),
]

CLASSES = [
    OutcomeClass(level=0, key="ON_TRACK", label="On Track", tone="success", description="Student is progressing well."),
    OutcomeClass(level=1, key="NEEDS_SUPPORT", label="Needs Improvement", tone="warning", description="Student would benefit from additional support."),
    OutcomeClass(level=2, key="AT_RISK", label="At Risk", tone="danger", description="High risk of failing; intervention required."),
]

DERIVED = {
    "academic_average": "Academic average: mean of assignment, previous exam and mock test scores",
}


def derive(x: Mapping[str, float | str]) -> dict[str, float]:
    avg = (float(x["assignment_score"]) + float(x["previous_exam_score"]) + float(x["mock_test_score"])) / 3
    return {"academic_average": round(avg, 2)}


def generate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    ability = rng.normal(0, 1, n)            # hidden aptitude
    motivation = rng.normal(0, 1, n)         # hidden engagement
    attendance = np.clip(80 + 9 * motivation + rng.normal(0, 7, n), 25, 100).round()
    study = np.clip(2.6 + 1.1 * motivation + rng.normal(0, 0.9, n), 0, 10).round(1)
    part_score = motivation + rng.normal(0, 0.7, n)
    participation = np.where(part_score < -0.5, "Low", np.where(part_score > 0.6, "High", "Medium"))
    assignment = np.clip(64 + 11 * ability + 8 * motivation + rng.normal(0, 9, n), 0, 100).round()
    prev = np.clip(60 + 15 * ability + 4 * motivation + rng.normal(0, 10, n), 0, 100).round()
    mock = np.clip(57 + 15 * ability + 6 * motivation + rng.normal(0, 11, n), 0, 100).round()
    backlogs = np.clip(rng.poisson(np.maximum(0.03, 0.45 - 0.6 * ability)), 0, 10)
    df = pd.DataFrame({
        "attendance": attendance, "study_hours": study, "participation": participation,
        "assignment_score": assignment, "previous_exam_score": prev, "mock_test_score": mock, "backlogs": backlogs,
    })
    latent = (
        -0.06 * (attendance - 80) - 0.35 * (study - 2.5)
        - 0.03 * (assignment - 60) - 0.045 * (prev - 60) - 0.05 * (mock - 55)
        + 0.45 * backlogs + 0.3 * (participation == "Low") - 0.2 * (participation == "High")
        + rng.normal(0, 0.45, n)
    )
    return finalize_labels(df, latent, (0.6, 2.1), RULES, derive, rng)


DOMAIN = DomainDefinition(
    id="education",
    name="Education",
    title="Student Performance Assessment",
    tagline="Academic performance prediction",
    description="Predicts a student's performance category and checks academic regulations - attendance requirement, pass marks and backlogs - to identify students requiring support.",
    icon="graduation-cap",
    task_type="Performance prediction (3-class)",
    subject="student",
    features=FEATURES,
    classes=CLASSES,
    rules=RULES,
    derive=derive,
    derived_features=DERIVED,
    generate=generate,
    presets=[
        ScenarioPreset(id="strong", name="Consistent performer", description="92% attendance, scores 80+",
                       inputs={"attendance": 92, "study_hours": 3.5, "participation": "High", "assignment_score": 84, "previous_exam_score": 81, "mock_test_score": 78, "backlogs": 0}),
        ScenarioPreset(id="struggling", name="Needs improvement", description="65% attendance, scores 40-50",
                       inputs={"attendance": 65, "study_hours": 2, "participation": "Medium", "assignment_score": 45, "previous_exam_score": 50, "mock_test_score": 40, "backlogs": 0}),
        ScenarioPreset(id="atrisk", name="At-risk student", description="55% attendance, 3 backlogs",
                       inputs={"attendance": 55, "study_hours": 1, "participation": "Low", "assignment_score": 38, "previous_exam_score": 33, "mock_test_score": 30, "backlogs": 3}),
    ],
    level_recommendations={
        0: ["Keep up the current study routine; consider advanced or enrichment material."],
        1: ["Provide additional learning resources.", "Recommend targeted practice tests.", "Monitor performance in the next assessment."],
        2: ["Arrange an immediate meeting with the student, mentor and parents.", "Create a personalised remedial plan with weekly progress checks."],
    },
    disclaimer="Decision-support output to assist faculty advisors; final academic decisions rest with the institution.",
)
