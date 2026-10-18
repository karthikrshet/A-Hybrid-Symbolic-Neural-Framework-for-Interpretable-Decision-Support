import time
from ai_engine.contracts.agent_schemas import AgentRequest, AgentResponse, AgentType
from ai_engine.inference.model_manager import model_manager

class NeuralAnalysisAgent:
    def __init__(self):
        self.agent_id = "agent-neural-01"
        self.agent_type = AgentType.NEURAL

    async def execute(self, request: AgentRequest) -> AgentResponse:
        start_t = time.time()
        prob, label, attributions = model_manager.predict(request.input_data)
        elapsed = (time.time() - start_t) * 1000.0
        
        return AgentResponse(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status="SUCCESS",
            confidence=float(prob),
            output={
                "risk_probability": float(prob),
                "risk_label": label,
                "model_version": model_manager.metadata.get("model_version", "1.0.0"),
                "algorithm": model_manager.metadata.get("algorithm", "RandomForest"),
                "feature_attributions": attributions
            },
            evidence=[{"type": "SHAP_ATTRIBUTION", "top_features": attributions[:3]}],
            execution_time_ms=elapsed
        )
