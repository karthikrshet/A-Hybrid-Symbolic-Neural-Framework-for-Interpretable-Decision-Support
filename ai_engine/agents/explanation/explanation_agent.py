import time
from ai_engine.contracts.agent_schemas import AgentRequest, AgentResponse, AgentType

class ExplanationAgent:
    def __init__(self):
        self.agent_id = "agent-explanation-01"
        self.agent_type = AgentType.EXPLANATION

    async def explain(
        self,
        request: AgentRequest,
        neural_res: AgentResponse,
        symbolic_res: AgentResponse,
        fusion_decision: str,
        fusion_reason: str,
        validation_res: AgentResponse
    ) -> AgentResponse:
        start_t = time.time()
        
        prob = neural_res.output.get("risk_probability", 0.0)
        rules = symbolic_res.output.get("triggered_rules", [])
        top_features = neural_res.output.get("feature_attributions", [])[:3]
        
        rule_desc = ", ".join([f"{r['rule_name']} ({r['severity']})" for r in rules]) if rules else "No compliance rules triggered"
        feature_desc = ", ".join([f"{f['feature_name']} (attribution: {f['attribution_score']:+.3f})" for f in top_features])
        
        summary = (
            f"Final Decision: {fusion_decision}. Rationale: {fusion_reason}. "
            f"The neural model evaluated risk probability at {prob:.1%}. "
            f"Key contributing features: {feature_desc}. "
            f"Symbolic rule evaluation: {rule_desc}. "
            f"Validation Status: {validation_res.output.get('validation_status')}."
        )
        
        elapsed = (time.time() - start_t) * 1000.0
        return AgentResponse(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status="SUCCESS",
            output={
                "summary": summary,
                "neural_basis": f"Calculated probability of {prob:.2%}",
                "symbolic_basis": rule_desc,
                "top_driving_features": top_features,
                "limitations": "Model predictions represent statistical correlations; compliance overrides take strict precedence."
            },
            evidence=[{"type": "AUDITABLE_SYNTHESIS", "summary": summary}],
            execution_time_ms=elapsed
        )
