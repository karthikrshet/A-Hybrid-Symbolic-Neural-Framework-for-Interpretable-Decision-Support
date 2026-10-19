import time
from ai_engine.contracts.agent_schemas import AgentRequest, AgentResponse, AgentType
from ai_engine.reasoning.rule_engine import rule_engine

class SymbolicReasoningAgent:
    def __init__(self):
        self.agent_id = "agent-symbolic-01"
        self.agent_type = AgentType.SYMBOLIC

    async def execute(self, request: AgentRequest) -> AgentResponse:
        start_t = time.time()
        triggered_rules, has_override, primary_action = rule_engine.evaluate(request.input_data)
        elapsed = (time.time() - start_t) * 1000.0
        
        return AgentResponse(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status="SUCCESS",
            confidence=1.0 if has_override else 0.85,
            output={
                "triggered_rules": [r.model_dump() for r in triggered_rules],
                "has_hard_override": has_override,
                "primary_action": primary_action,
                "rules_evaluated_count": len(rule_engine.rules)
            },
            evidence=[{"type": "TRIGGERED_RULES", "rules": [r.rule_id for r in triggered_rules]}],
            execution_time_ms=elapsed
        )
