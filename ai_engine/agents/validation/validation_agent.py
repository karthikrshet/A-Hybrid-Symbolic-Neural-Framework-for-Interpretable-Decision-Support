import time
from ai_engine.contracts.agent_schemas import AgentRequest, AgentResponse, AgentType

class ValidationAgent:
    def __init__(self):
        self.agent_id = "agent-validation-01"
        self.agent_type = AgentType.VALIDATION

    async def validate(self, request: AgentRequest, neural_res: AgentResponse, symbolic_res: AgentResponse, fusion_decision: str) -> AgentResponse:
        start_t = time.time()
        issues = []
        is_valid = True
        
        # Check 1: Input presence
        if "transaction_amount" not in request.input_data:
            issues.append("Missing mandatory transaction_amount")
            is_valid = False
            
        # Check 2: Neural risk bounds
        prob = neural_res.output.get("risk_probability", -1.0)
        if not (0.0 <= prob <= 1.0):
            issues.append(f"Invalid probability value out of [0, 1] range: {prob}")
            is_valid = False
            
        # Check 3: Override consistency
        has_override = symbolic_res.output.get("has_hard_override", False)
        if has_override and fusion_decision != "REJECT":
            issues.append("Inconsistency: Hard constraint violated but fusion outcome did not reject transaction")
            is_valid = False
            
        elapsed = (time.time() - start_t) * 1000.0
        status = "VALID" if is_valid else "INVALID"
        
        return AgentResponse(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status=status,
            confidence=1.0 if is_valid else 0.0,
            output={"validation_status": status, "issues": issues, "checks_performed": 3},
            evidence=[{"type": "INTEGRITY_CHECK", "passed": is_valid}],
            execution_time_ms=elapsed
        )
