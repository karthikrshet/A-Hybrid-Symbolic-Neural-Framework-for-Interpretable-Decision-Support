import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.domain import TransactionInput, DecisionResponse
from backend.app.models.entities import DecisionRecord
from backend.app.services.audit_service import AuditService
from ai_engine.orchestration.coordinator import coordinator

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.post("/analyze", response_model=DecisionResponse)
async def analyze_transaction(tx_input: TransactionInput, db: Session = Depends(get_db)):
    data = tx_input.dict()
    result = await coordinator.execute_decision_pipeline(data)
    
    # Persist DecisionRecord
    record = DecisionRecord(
        id=result["decision_id"],
        correlation_id=result["correlation_id"],
        input_payload=json.dumps(data),
        final_decision=result["final_decision"],
        confidence_score=result["confidence_score"],
        neural_score=result["neural_analysis"].get("risk_probability", 0.0),
        symbolic_rules_triggered=json.dumps(result["symbolic_analysis"].get("triggered_rules", [])),
        rule_override=result["symbolic_analysis"].get("has_hard_override", False),
        human_review_required=result["requires_human_review"],
        explanation_summary=result["explanation"].get("summary", ""),
        execution_trace_json=json.dumps(result["execution_trace"]),
        latency_ms=result["latency_ms"]
    )
    db.add(record)
    db.commit()
    
    # Audit log
    AuditService.record_event(
        db, entity_type="DECISION", entity_id=record.id, action="DECISION_CREATED",
        actor="COORDINATOR", payload={"decision": record.final_decision, "confidence": record.confidence_score}
    )
    
    return result

@router.get("/history")
def get_decision_history(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(DecisionRecord).order_by(DecisionRecord.created_at.desc()).limit(limit).all()
    out = []
    for r in records:
        out.append({
            "id": r.id,
            "correlation_id": r.correlation_id,
            "decision": r.final_decision,
            "confidence": r.confidence_score,
            "neural_score": r.neural_score,
            "rule_override": r.rule_override,
            "human_review_required": r.human_review_required,
            "explanation": r.explanation_summary,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at.isoformat()
        })
    return out
