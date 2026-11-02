import time
from ai_engine.contracts.agent_schemas import AgentRequest, AgentResponse, AgentType
from ai_engine.explainability.llm_explainer import llm_service
from ai_engine.explainability.contrastive import ContrastiveExplainer

class ExplanationAgent:
    def __init__(self):
        self.agent_id = "agent-explanation-01"
        self.agent_type = AgentType.EXPLANATION
        self.llm_service = llm_service

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
        has_override = symbolic_res.output.get("has_hard_override", False)
        top_features = neural_res.output.get("feature_attributions", [])[:5]
        
        # Synthesize via LLM / Grounded XAI
        narrative_summary = self.llm_service.synthesize_explanation(
            decision=fusion_decision,
            confidence=neural_res.confidence,
            reason=fusion_reason,
            neural_prob=prob,
            top_features=top_features,
            rules=rules,
            is_override=has_override
        )

        # Generate actionable counterfactual recommendations
        recommendations = ContrastiveExplainer.generate_counterfactuals(
            decision=fusion_decision,
            features=request.input_data,
            triggered_rules=[r.get("rule_name") for r in rules]
        )
        
        elapsed = (time.time() - start_t) * 1000.0
        return AgentResponse(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status="SUCCESS",
            output={
                "summary": narrative_summary,
                "provider": self.llm_service.provider,
                "neural_basis": f"Calibrated risk probability of {prob:.2%}",
                "symbolic_basis": [r.get("rule_name") for r in rules],
                "top_driving_features": top_features,
                "counterfactual_recommendations": recommendations,
                "limitations": "Model predictions represent statistical correlations; compliance overrides take strict precedence."
            },
            evidence=[{"type": "AUDITABLE_SYNTHESIS", "summary": narrative_summary}],
            execution_time_ms=elapsed
        )
