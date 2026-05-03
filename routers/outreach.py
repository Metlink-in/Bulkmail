from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from database import get_db
from middleware.auth_middleware import require_user
from utils.helpers import get_current_timestamp, json_safe

router = APIRouter(tags=["outreach"])


class OutreachRecipient(BaseModel):
    email: str
    first_name: str = ""
    last_name:  str = ""
    company:    str = ""
    custom_1:   str = ""
    custom_2:   str = ""
    custom_3:   str = ""


class OutreachSendBody(BaseModel):
    campaign_name:    str
    subject:          str
    html_body:        str
    recipients:       List[OutreachRecipient]
    sender_profile_id: Optional[str] = None
    interval_seconds: int = 120
    daily_limit:      int = 500


class OutreachPreviewBody(BaseModel):
    subject:   str
    html_body: str
    recipient: OutreachRecipient


@router.post("/preview")
async def preview_outreach(
    body: OutreachPreviewBody,
    current_user: Dict[str, Any] = Depends(require_user)
):
    r = body.recipient
    first_name = r.first_name or r.email.split("@")[0]
    last_name  = r.last_name or ""
    full_name  = f"{first_name} {last_name}".strip()
    company    = r.company or ""

    tokens = {
        "{first_name}": first_name,
        "{last_name}":  last_name,
        "{full_name}":  full_name,
        "{company}":    company,
        "{org}":        company,
        "{email}":      r.email,
        "{custom_1}":   r.custom_1 or "",
        "{custom_2}":   r.custom_2 or "",
        "{custom_3}":   r.custom_3 or "",
    }

    resolved_subject = body.subject
    resolved_html    = body.html_body
    for token, val in tokens.items():
        resolved_subject = resolved_subject.replace(token, val)
        resolved_html    = resolved_html.replace(token, val)

    return {"subject": resolved_subject, "html": resolved_html}


@router.post("/send")
async def create_outreach_job(
    body: OutreachSendBody,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    if not body.recipients:
        raise HTTPException(status_code=400, detail="No recipients provided")
    if not body.subject.strip():
        raise HTTPException(status_code=400, detail="Subject is required")
    if not body.html_body.strip():
        raise HTTPException(status_code=400, detail="Email body is required")

    user_id = str(current_user["_id"])
    now     = get_current_timestamp()

    job = {
        "_id":              str(uuid.uuid4()),
        "user_id":          user_id,
        "job_type":         "outreach",
        "campaign_name":    body.campaign_name or "Custom Outreach",
        "subject":          body.subject,
        "html_body":        body.html_body,
        "inline_recipients": [r.dict() for r in body.recipients],
        "sender_profile_id": body.sender_profile_id,
        "interval_seconds": max(60, body.interval_seconds),
        "daily_limit":      body.daily_limit,
        "status":           "queued",
        "total_count":      len(body.recipients),
        "sent_count":       0,
        "failed_count":     0,
        "created_at":       now,
        "updated_at":       now,
    }

    await db.mail_jobs.insert_one(job)
    return json_safe({"job_id": job["_id"], "total": len(body.recipients), "message": "Outreach queued"})


@router.post("/tick/{job_id}")
async def tick_outreach(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    from services.mail_service import tick_outreach_job
    user_id = str(current_user["_id"])
    result  = await tick_outreach_job(db, user_id, job_id)
    return json_safe(result)


@router.get("/{job_id}/status")
async def outreach_job_status(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    job = await db.mail_jobs.find_one({"_id": job_id, "user_id": user_id, "job_type": "outreach"})
    if not job:
        raise HTTPException(status_code=404, detail="Outreach job not found")
    from services.mail_service import _outreach_status
    return json_safe(await _outreach_status(db, job_id, job))


@router.post("/{job_id}/cancel")
async def cancel_outreach(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    res = await db.mail_jobs.update_one(
        {"_id": job_id, "user_id": user_id, "status": {"$in": ["queued", "running", "paused"]}},
        {"$set": {"status": "cancelled", "updated_at": get_current_timestamp()}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found or already finished")
    return {"message": "Outreach cancelled"}
