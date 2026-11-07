"""IT troubleshooting domain - software failure detection and recovery suggestions."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from app.domains.base import DomainDefinition, finalize_labels
from app.domains.it_troubleshooting.rules import RULES
from app.schemas import FeatureSpec, OutcomeClass, ScenarioPreset

FEATURES = [
    FeatureSpec(name="cpu_utilization", label="CPU utilisation", kind="number", unit="%", min=0, max=100, step=1, default=95, group="Resources"),
    FeatureSpec(name="memory_utilization", label="Memory utilisation", kind="number", unit="%", min=0, max=100, step=1, default=92, group="Resources"),
    FeatureSpec(name="disk_utilization", label="Disk utilisation", kind="number", unit="%", min=0, max=100, step=1, default=60, group="Resources"),
    FeatureSpec(name="response_time_ms", label="API response time", kind="number", unit="ms", min=10, max=20000, step=10, default=8000, group="Performance"),
    FeatureSpec(name="error_rate", label="Error rate", kind="number", unit="%", min=0, max=100, step=0.1, default=25, group="Performance"),
    FeatureSpec(name="throughput_rps", label="Throughput", kind="number", unit="req/s", min=0, max=5000, step=10, default=420, group="Performance"),
    FeatureSpec(name="restarts_last_hour", label="Restarts (last hour)", kind="number", unit="", min=0, max=20, step=1, default=1, group="Stability"),
    FeatureSpec(name="service_status", label="Service status", kind="select", options=["Healthy", "Degraded", "Unhealthy"], default="Unhealthy", group="Stability"),
]

CLASSES = [
    OutcomeClass(level=0, key="HEALTHY", label="Healthy", tone="success", description="System operating within normal parameters."),
    OutcomeClass(level=1, key="DEGRADED", label="Service Degradation", tone="warning", description="Abnormal behaviour detected; investigation recommended."),
    OutcomeClass(level=2, key="CRITICAL", label="Critical Failure Risk", tone="danger", description="Critical system condition; immediate action required."),
]

DERIVED = {
    "resource_pressure": "Resource pressure: mean of CPU, memory and disk utilisation (%)",
    "latency_seconds": "Latency: API response time in seconds",
}


def derive(x: Mapping[str, float | str]) -> dict[str, float]:
    pressure = (float(x["cpu_utilization"]) + float(x["memory_utilization"]) + float(x["disk_utilization"])) / 3
    return {"resource_pressure": round(pressure, 2), "latency_seconds": round(float(x["response_time_ms"]) / 1000, 3)}


def generate(n: int, rng: np.random.Generator) -> pd.DataFrame:
    load = rng.beta(2.2, 3.0, n)  # hidden workload intensity 0..1
    fault = rng.random(n) < 0.18   # hidden fault (bad deploy, leak, dependency outage)
    cpu = np.clip(25 + 70 * load + rng.normal(0, 9, n) + 8 * fault, 1, 100).round()
    mem = np.clip(35 + 50 * load + rng.normal(0, 10, n) + 14 * fault * rng.random(n), 5, 100).round()
    disk = np.clip(rng.normal(58, 17, n), 10, 100).round()
    resp = np.clip(rng.lognormal(np.log(180 + 2600 * load ** 3 + 2500 * fault), 0.55, n), 15, 19900).round(-1)
    err = np.clip(rng.lognormal(np.log(0.6 + 4 * load ** 2 + 9 * fault), 0.7, n), 0, 100).round(1)
    rps = np.clip(rng.normal(300 + 1800 * load, 250, n) * np.where(fault, 0.7, 1.0), 0, 5000).round(-1)
    restarts = np.clip(rng.poisson(0.2 + 3.5 * fault * rng.random(n)), 0, 20)
    p_unhealthy = np.clip(0.01 + 0.35 * fault + 0.05 * (err > 15), 0, 1)
    p_degraded = np.clip(0.06 + 0.25 * load + 0.2 * fault, 0, 1)
    u = rng.random(n)
    status = np.where(u < p_unhealthy, "Unhealthy", np.where(u < p_unhealthy + p_degraded, "Degraded", "Healthy"))
    df = pd.DataFrame({
        "cpu_utilization": cpu, "memory_utilization": mem, "disk_utilization": disk,
        "response_time_ms": resp, "error_rate": err, "throughput_rps": rps,
        "restarts_last_hour": restarts, "service_status": status,
    })
    latent = (
        0.045 * (cpu - 60) + 0.04 * (mem - 60) + 0.03 * np.maximum(disk - 75, 0)
        + 0.9 * np.log(resp / 400) + 0.11 * err + 0.35 * restarts
        + 1.0 * (status == "Degraded") + 2.0 * (status == "Unhealthy")
        + rng.normal(0, 0.5, n)
    )
    return finalize_labels(df, latent, (1.6, 3.6), RULES, derive, rng)


DOMAIN = DomainDefinition(
    id="it_troubleshooting",
    name="IT Troubleshooting",
    title="Software Failure Detection",
    tagline="Failure detection & recovery decisions",
    description="Analyses application-health metrics to detect abnormal behaviour, identifies violated SRE monitoring rules and suggests corrective actions.",
    icon="server-cog",
    task_type="Anomaly / failure classification (3-class)",
    subject="service",
    features=FEATURES,
    classes=CLASSES,
    rules=RULES,
    derive=derive,
    derived_features=DERIVED,
    generate=generate,
    presets=[
        ScenarioPreset(id="normal", name="Normal operation", description="Low utilisation, fast responses",
                       inputs={"cpu_utilization": 38, "memory_utilization": 52, "disk_utilization": 48, "response_time_ms": 180, "error_rate": 0.4, "throughput_rps": 650, "restarts_last_hour": 0, "service_status": "Healthy"}),
        ScenarioPreset(id="slow", name="Latency spike", description="CPU 88%, 3.8 s responses",
                       inputs={"cpu_utilization": 88, "memory_utilization": 76, "disk_utilization": 61, "response_time_ms": 3800, "error_rate": 4.2, "throughput_rps": 1300, "restarts_last_hour": 1, "service_status": "Degraded"}),
        ScenarioPreset(id="outage", name="Critical outage", description="CPU 95%, memory 92%, 25% errors",
                       inputs={"cpu_utilization": 95, "memory_utilization": 92, "disk_utilization": 60, "response_time_ms": 8000, "error_rate": 25, "throughput_rps": 420, "restarts_last_hour": 4, "service_status": "Unhealthy"}),
    ],
    level_recommendations={
        0: ["No action needed; continue routine monitoring."],
        1: ["Open an investigation ticket and watch the flagged metrics closely.", "Correlate the anomaly with recent deployments or traffic changes."],
        2: ["Page the on-call engineer and start the incident runbook.", "Consider a controlled service restart only if diagnostics justify it."],
    },
    disclaimer="Automated diagnosis is a recommendation; verify with logs and monitoring before taking corrective action.",
)
