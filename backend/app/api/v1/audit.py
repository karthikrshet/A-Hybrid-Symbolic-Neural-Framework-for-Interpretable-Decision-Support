from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.entities import AuditLogEntry
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("/logs")
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    entries = db.query(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc()).limit(limit).all()
    return [{
        "id": e.id,
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "action": e.action,
        "actor": e.actor,
        "payload_hash": e.payload_hash,
        "prev_hash": e.prev_hash,
        "timestamp": e.timestamp.isoformat()
    } for e in entries]

@router.get("/verify")
def verify_audit_integrity(db: Session = Depends(get_db)):
    is_valid = AuditService.verify_integrity(db)
    return {"chain_valid": is_valid, "algorithm": "SHA-256", "status": "VERIFIED" if is_valid else "CORRUPTED"}
