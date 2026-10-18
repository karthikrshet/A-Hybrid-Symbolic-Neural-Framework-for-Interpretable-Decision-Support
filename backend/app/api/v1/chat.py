import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.domain import ChatMessageRequest, ChatMessageResponse
from backend.app.models.entities import Conversation, Message
from ai_engine.orchestration.coordinator import coordinator

router = APIRouter(prefix="/chat", tags=["Conversational Intelligence"])

@router.post("/message", response_model=ChatMessageResponse)
async def process_chat_message(chat_req: ChatMessageRequest, db: Session = Depends(get_db)):
    conv_id = chat_req.conversation_id or str(uuid.uuid4())
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        conv = Conversation(id=conv_id, title=chat_req.message[:35] + "...")
        db.add(conv)
        db.commit()

    # User message
    u_msg = Message(conversation_id=conv_id, sender="USER", content=chat_req.message)
    db.add(u_msg)
    db.commit()

    # If structured context supplied or query asks about risk
    decision_result = None
    if chat_req.structured_context:
        decision_result = await coordinator.execute_decision_pipeline(chat_req.structured_context)
        reply = (
            f"Evaluated transaction context: {decision_result['final_decision']}. "
            f"Confidence: {decision_result['confidence_score']:.1%}. "
            f"{decision_result['explanation']['summary']}"
        )
    else:
        reply = (
            f"Coordinator classified your query. The Neuro-Symbolic engine is ready to evaluate financial transactions, "
            f"audit compliance rules, or compare neural baselines. Submit transaction parameters or ask domain questions."
        )

    a_msg = Message(conversation_id=conv_id, sender="ASSISTANT", content=reply)
    db.add(a_msg)
    db.commit()

    return ChatMessageResponse(
        conversation_id=conv_id,
        reply=reply,
        workflow_state="COMPLETED",
        decision=decision_result,
        agent_traces=decision_result["execution_trace"] if decision_result else []
    )
