import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.entities import AuditLogEntry

class AuditService:
    @staticmethod
    def calculate_hash(data: dict, prev_hash: str = "") -> str:
        serialized = json.dumps(data, sort_keys=True) + prev_hash
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def record_event(cls, db: Session, entity_type: str, entity_id: str, action: str, actor: str, payload: dict) -> AuditLogEntry:
        last_entry = db.query(AuditLogEntry).order_by(AuditLogEntry.timestamp.desc()).first()
        prev_hash = last_entry.payload_hash if last_entry else "0" * 64
        payload_hash = cls.calculate_hash(payload, prev_hash)
        
        entry = AuditLogEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            payload_hash=payload_hash,
            prev_hash=prev_hash,
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @classmethod
    def verify_integrity(cls, db: Session) -> bool:
        entries = db.query(AuditLogEntry).order_by(AuditLogEntry.timestamp.asc()).all()
        current_prev = "0" * 64
        for entry in entries:
            if entry.prev_hash != current_prev:
                return False
            current_prev = entry.payload_hash
        return True

# Step refinement 6
# Actor indexing metadata

# Step refinement 16
# Actor indexing metadata

# Step refinement 26
# Actor indexing metadata

# Step refinement 36
# Actor indexing metadata
