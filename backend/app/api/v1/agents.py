import time
from fastapi import APIRouter
from ai_engine.orchestration.coordinator import coordinator
from ai_engine.reasoning.rule_engine import rule_engine
from ai_engine.inference.model_manager import model_manager
from ai_engine.contracts.agent_schemas import WorkflowState, AgentType

router = APIRouter(prefix="/agents", tags=["Specialized Agents"])

@router.get("")
@router.get("/")
def list_agents():
    # Introspect live agent instances dynamically from memory
    agents_list = [
        {
            "agent_id": "agent-coordinator-main",
            "name": coordinator.__class__.__name__,
            "type": AgentType.COORDINATOR.value,
            "paradigm": "Finite State Machine (FSM) Controller",
            "status": "ONLINE" if coordinator is not None else "OFFLINE",
            "supported_workflow_states": [s.value for s in WorkflowState],
            "registered_subagents": [
                coordinator.neural_agent.agent_id,
                coordinator.symbolic_agent.agent_id,
                coordinator.validation_agent.agent_id,
                coordinator.explanation_agent.agent_id
            ]
        },
        {
            "agent_id": coordinator.neural_agent.agent_id,
            "name": coordinator.neural_agent.__class__.__name__,
            "type": coordinator.neural_agent.agent_type.value,
            "paradigm": "Trained Machine Learning Inference & TreeSHAP",
            "status": "ONLINE" if model_manager.model is not None else "OFFLINE",
            "model_version": model_manager.metadata.get("model_version", "unknown"),
            "algorithm": model_manager.metadata.get("algorithm", "unknown"),
            "features_utilized": model_manager.metadata.get("features", []),
            "training_samples": model_manager.metadata.get("training_samples", 0),
            "model_metrics": model_manager.metadata.get("metrics", {})
        },
        {
            "agent_id": coordinator.symbolic_agent.agent_id,
            "name": coordinator.symbolic_agent.__class__.__name__,
            "type": coordinator.symbolic_agent.agent_type.value,
            "paradigm": "Deterministic Forward-Chaining Knowledge Base",
            "status": "ONLINE" if len(rule_engine.rules) > 0 else "OFFLINE",
            "rules_filepath": rule_engine.rules_filepath,
            "active_rules_count": len(rule_engine.rules),
            "rule_identifiers": [r.get("rule_id") for r in rule_engine.rules]
        },
        {
            "agent_id": coordinator.validation_agent.agent_id,
            "name": coordinator.validation_agent.__class__.__name__,
            "type": coordinator.validation_agent.agent_type.value,
            "paradigm": "Boundary & Evidence Invariant Verification",
            "status": "ONLINE",
            "checks_enforced": [
                "Mandatory input existence",
                "Calibrated probability bound in [0.0, 1.0]",
                "Hard constraint override consistency"
            ]
        },
        {
            "agent_id": coordinator.explanation_agent.agent_id,
            "name": coordinator.explanation_agent.__class__.__name__,
            "type": coordinator.explanation_agent.agent_type.value,
            "paradigm": "Grounded XAI Narrative Synthesis",
            "status": "ONLINE",
            "capabilities": [
                "Top driving feature attributions extraction",
                "Symbolic compliance rationale translation",
                "Limitation and uncertainty disclosure"
            ]
        }
    ]

    return {
        "total_registered_agents": len(agents_list),
        "agents": agents_list
    }

@router.get("/health")
def agents_health():
    # Dynamically probe each live component
    return {
        "status": "HEALTHY",
        "coordinator": "ONLINE" if coordinator is not None else "OFFLINE",
        "neural_agent": "ONLINE" if model_manager.model is not None else "OFFLINE",
        "symbolic_agent": "ONLINE" if len(rule_engine.rules) > 0 else "OFFLINE",
        "validation_agent": "ONLINE" if coordinator.validation_agent is not None else "OFFLINE",
        "explanation_agent": "ONLINE" if coordinator.explanation_agent is not None else "OFFLINE"
    }
