from typing import Dict, Any, List, Tuple
from ai_engine.contracts.agent_schemas import DecisionOutcome, TriggeredRuleInfo

class DecisionFusionEngine:
    def __init__(self):
        self.fusion_policy_version = "2.1.0-conflict-aware"

    def fuse(
        self,
        neural_prob: float,
        neural_label: str,
        triggered_rules: List[TriggeredRuleInfo],
        has_hard_override: bool
    ) -> Tuple[DecisionOutcome, float, bool, str]:
        
        # Policy 1: Hard constraint overrides probability unconditionally
        if has_hard_override:
            override_rules = [r.rule_name for r in triggered_rules if r.override_applied]
            reason = f"SYMBOLIC_OVERRIDE: Hard regulatory/compliance violation triggered ({', '.join(override_rules)}). Neural risk: {neural_prob:.2f} superseded."
            return DecisionOutcome.REJECT, 0.99, True, reason

        # Policy 2: High Neural Risk (> 0.70)
        if neural_prob >= 0.70:
            if any(r.severity == "HIGH_RISK_SOFT" for r in triggered_rules):
                reason = f"Consensus Rejection: Neural prediction ({neural_prob:.2f}) and symbolic risk heuristics both flag high hazard."
                return DecisionOutcome.REJECT, neural_prob, False, reason
            else:
                reason = f"Neural Precaution: Statistical model detected high risk pattern ({neural_prob:.2f}) despite absence of explicit rule trigger."
                return DecisionOutcome.FLAG_SUSPICIOUS, neural_prob, True, reason

        # Policy 3: Borderline Epistemic Uncertainty (0.30 - 0.70)
        if 0.30 <= neural_prob < 0.70:
            reason = f"Epistemic Uncertainty: Calibrated risk score ({neural_prob:.2f}) resides in borderline region. Requires compliance officer adjudication."
            return DecisionOutcome.REQUIRES_HUMAN_REVIEW, neural_prob, True, reason

        # Policy 4: Low Neural Risk (< 0.30) with Soft Rule Warnings
        if any(r.severity in ["HIGH_RISK_SOFT", "MEDIUM_RISK_SOFT"] for r in triggered_rules):
            reason = f"Precautionary Monitoring: Low neural risk ({neural_prob:.2f}) but symbolic soft anomaly flags require monitoring."
            return DecisionOutcome.FLAG_MONITOR, 0.75, False, reason

        # Policy 5: Low Risk Clear Consensus
        reason = f"Full Consensus Clearance: Low statistical risk ({neural_prob:.2f}) and zero compliance or velocity rule violations."
        return DecisionOutcome.APPROVE, 0.95, False, reason

fusion_engine = DecisionFusionEngine()
