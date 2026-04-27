from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.services.ai_service import compose_email, improve_email

router = APIRouter(tags=["ai"])

class AiComposeRequest(BaseModel):
    goal: str
    industry: str
    tone: str
    sender_name: str
    sender_company: str
    value_prop: str
    recipient_name: Optional[str] = "there"

class AiImproveRequest(BaseModel):
    current_subject: str
    current_html_body: str
    instruction: str

@router.post("/compose")
async def ai_compose(body: AiComposeRequest, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await compose_email(
        db, user_id, body.goal, body.industry, body.tone,
        body.sender_name, body.sender_company, body.value_prop, body.recipient_name
    )
    return res

@router.post("/improve")
async def ai_improve(body: AiImproveRequest, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await improve_email(
        db, user_id, body.current_subject, body.current_html_body, body.instruction
    )
    return res
