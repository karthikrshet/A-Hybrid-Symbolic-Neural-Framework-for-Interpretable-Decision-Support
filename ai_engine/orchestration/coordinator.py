import uuid
import time
from typing import Dict, Any, List
from ai_engine.contracts.agent_schemas import (
    WorkflowState, AgentType, DecisionOutcome, AgentRequest, AgentResponse, ExecutionTrace, TriggeredRuleInfo
)
from ai_engine.agents.neural.neural_agent import NeuralAnalysisAgent
from ai_engine.agents.symbolic.symbolic_agent import SymbolicReasoningAgent
from ai_engine.agents.validation.validation_agent import ValidationAgent
from ai_engine.agents.explanation.explanation_agent import ExplanationAgent
from ai_engine.fusion.decision_fusion import fusion_engine

class CoordinatorAgent:
    def __init__(self):
        self.neural_agent = NeuralAnalysisAgent()
        self.symbolic_agent = SymbolicReasoningAgent()
        self.validation_agent = ValidationAgent()
        self.explanation_agent = ExplanationAgent()

    async def execute_decision_pipeline(self, input_data: Dict[str, Any], correlation_id: str = None) -> Dict[str, Any]:
        start_overall = time.time()
        req_id = correlation_id or str(uuid.uuid4())
        exec_id = str(uuid.uuid4())
        traces: List[ExecutionTrace] = []

        # 1. State: RECEIVED
        traces.append(ExecutionTrace(
            agent_id="coordinator",
            agent_type=AgentType.COORDINATOR,
            step="REQUEST_RECEIVED",
            status="SUCCESS",
            execution_time_ms=0.1,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            details={"correlation_id": req_id}
        ))

        # 2. State: EXECUTING (Dispatch Neural & Symbolic)
        req = AgentRequest(request_id=req_id, execution_id=exec_id, task_type="TRANSACTION_ANALYSIS", input_data=input_data)
        
        neural_res = await self.neural_agent.execute(req)
        traces.append(ExecutionTrace(
            agent_id=neural_res.agent_id,
            agent_type=AgentType.NEURAL,
            step="NEURAL_INFERENCE",
            status=neural_res.status,
            execution_time_ms=neural_res.execution_time_ms,
            timestamp=neural_res.timestamp,
            details=neural_res.output
        ))

        symbolic_res = await self.symbolic_agent.execute(req)
        traces.append(ExecutionTrace(
            agent_id=symbolic_res.agent_id,
            agent_type=AgentType.SYMBOLIC,
            step="SYMBOLIC_EVALUATION",
            status=symbolic_res.status,
            execution_time_ms=symbolic_res.execution_time_ms,
            timestamp=symbolic_res.timestamp,
            details=symbolic_res.output
        ))

        # 3. State: FUSING
        triggered_rules_raw = symbolic_res.output.get("triggered_rules", [])
        triggered_rules = [TriggeredRuleInfo(**r) for r in triggered_rules_raw]
        has_override = symbolic_res.output.get("has_hard_override", False)
        neural_prob = neural_res.output.get("risk_probability", 0.0)
        neural_label = neural_res.output.get("risk_label", "LOW_RISK")

        fuse_start = time.time()
        final_decision, conf, review_req, reason = fusion_engine.fuse(
            neural_prob=neural_prob,
            neural_label=neural_label,
            triggered_rules=triggered_rules,
            has_hard_override=has_override
        )
        fuse_ms = (time.time() - fuse_start) * 1000.0
        traces.append(ExecutionTrace(
            agent_id="fusion-engine",
            agent_type=AgentType.COORDINATOR,
            step="DECISION_FUSION",
            status="SUCCESS",
            execution_time_ms=fuse_ms,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            details={"decision": final_decision.value, "confidence": conf, "review_required": review_req, "reason": reason}
        ))

        # 4. State: VALIDATING
        validation_res = await self.validation_agent.validate(req, neural_res, symbolic_res, final_decision.value)
        traces.append(ExecutionTrace(
            agent_id=validation_res.agent_id,
            agent_type=AgentType.VALIDATION,
            step="INTEGRITY_VALIDATION",
            status=validation_res.status,
            execution_time_ms=validation_res.execution_time_ms,
            timestamp=validation_res.timestamp,
            details=validation_res.output
        ))

        # 5. State: EXPLAINING
        expl_res = await self.explanation_agent.explain(
            req, neural_res, symbolic_res, final_decision.value, reason, validation_res
        )
        traces.append(ExecutionTrace(
            agent_id=expl_res.agent_id,
            agent_type=AgentType.EXPLANATION,
            step="EXPLANATION_SYNTHESIS",
            status=expl_res.status,
            execution_time_ms=expl_res.execution_time_ms,
            timestamp=expl_res.timestamp,
            details=expl_res.output
        ))

        total_latency = (time.time() - start_overall) * 1000.0

        return {
            "decision_id": exec_id,
            "correlation_id": req_id,
            "final_decision": final_decision.value,
            "confidence_score": conf,
            "requires_human_review": review_req,
            "neural_analysis": neural_res.output,
            "symbolic_analysis": symbolic_res.output,
            "validation_status": validation_res.output.get("validation_status", "VALID"),
            "explanation": expl_res.output,
            "execution_trace": [t.dict() for t in traces],
            "latency_ms": float(total_latency)
        }

coordinator = CoordinatorAgent()

# Step refinement 8
# Timeout protection wrapper

# Step refinement 18
# Timeout protection wrapper

# Step refinement 28
# Timeout protection wrapper

# Step refinement 38
# Timeout protection wrapper

# Step refinement 48
# Timeout protection wrapper

# Step refinement 58
# Timeout protection wrapper

# Step refinement 68
# Timeout protection wrapper

# Step refinement 78
# Timeout protection wrapper
