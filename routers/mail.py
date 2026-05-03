from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import uuid
import os

from database import get_db
from middleware.auth_middleware import require_user
from services.mail_service import (
    pause_job, resume_job, cancel_job, get_job_status, tick_mail_job,
    send_single_email, build_email_message, get_user_smtp_settings
)
from utils.helpers import get_current_timestamp, json_safe

_IS_VERCEL = bool(os.environ.get("VERCEL"))

router = APIRouter(tags=["mail"])

class MailJobCreate(BaseModel):
    sender_profile_id: Optional[str] = None
    template_id: str
    contact_list_id: Optional[str] = None
    contact_ids: Optional[List[str]] = None
    schedule_at: Optional[datetime] = None
    interval_seconds: Optional[int] = 300
    daily_limit: Optional[int] = 500
    from_name_override: Optional[str] = None
    reply_to_override: Optional[str] = None
    attachments_base64: Optional[List[dict]] = []

class TestMailRequest(BaseModel):
    to_email: str
    template_id: str

@router.post("/jobs")
async def create_mail_job(body: MailJobCreate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])

    # Validate template exists and belongs to this user (or is global)
    template = await db.mail_templates.find_one({"_id": body.template_id, "user_id": user_id})
    if not template:
        template = await db.mail_templates.find_one({"_id": body.template_id, "is_global": True})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Validate contact list exists if provided
    if body.contact_list_id:
        c_list = await db.contact_lists.find_one({"_id": body.contact_list_id, "user_id": user_id})
        if not c_list:
            raise HTTPException(status_code=404, detail="Contact list not found")

    job_id = str(uuid.uuid4())

    now = get_current_timestamp()
    scheduled_at = body.schedule_at if body.schedule_at else now + timedelta(seconds=5)

    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "sender_profile_id": body.sender_profile_id,
        "template_id": body.template_id,
        "contact_list_id": body.contact_list_id,
        "contact_ids": body.contact_ids or [],
        "status": "queued",
        "scheduled_at": scheduled_at,
        "interval_seconds": body.interval_seconds,
        "daily_limit": body.daily_limit,
        "from_name_override": body.from_name_override,
        "reply_to_override": body.reply_to_override,
        "attachments_base64": body.attachments_base64,
        "total_recipients": 0,
        "created_at": now,
        "updated_at": now
    }
    
    await db.mail_jobs.insert_one(job_doc)

    total = 0
    if body.contact_list_id:
        total = await db.contacts.count_documents({"list_id": body.contact_list_id})
    elif body.contact_ids:
        total = len(body.contact_ids)

    if total:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"total_recipients": total}})

    if not _IS_VERCEL:
        from services.scheduler_service import schedule_job
        await schedule_job(db, job_id, scheduled_at)
    # On Vercel: the client's tick polling drives execution — no scheduler needed

    return json_safe({
        "job_id": job_id,
        "status": "queued",
        "total_recipients": total,
        "scheduled_at": scheduled_at
    })

@router.get("/jobs")
async def get_mail_jobs(
    page: int = 1, limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    query: Dict[str, Any] = {"user_id": user_id}
    if status:
        query["status"] = status
    if search:
        query["_id"] = {"$regex": search, "$options": "i"}

    skip = (page - 1) * limit
    cursor = db.mail_jobs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)

    if jobs:
        job_ids = [j["_id"] for j in jobs]
        pipeline = [
            {"$match": {"job_id": {"$in": job_ids}, "user_id": user_id}},
            {"$group": {
                "_id": "$job_id",
                "sent_count":   {"$sum": {"$cond": [{"$eq": ["$status", "sent"]}, 1, 0]}},
                "failed_count": {"$sum": {"$cond": [{"$ne": ["$status", "sent"]}, 1, 0]}},
                "log_total":    {"$sum": 1}
            }}
        ]
        stats = await db.mail_logs.aggregate(pipeline).to_list(None)
        stats_map = {s["_id"]: s for s in stats}

        for j in jobs:
            s = stats_map.get(j["_id"], {})
            j["sent_count"]   = s.get("sent_count", 0)
            j["failed_count"] = s.get("failed_count", 0)
            j["total_count"]  = j.get("total_recipients") or s.get("log_total", 0)

    return json_safe(jobs)

@router.get("/jobs/{job_id}")
async def get_mail_job_details(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    job = await db.mail_jobs.find_one({"_id": job_id, "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    logs = await db.mail_logs.find({"job_id": job_id, "user_id": user_id}).sort("sent_at", -1).limit(20).to_list(None)
    job["recent_logs"] = logs
    return json_safe(job)

@router.get("/jobs/{job_id}/status")
async def poll_job_status(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    return json_safe(await get_job_status(db, user_id, job_id))

@router.post("/jobs/{job_id}/tick")
async def tick_job(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    """Serverless-friendly: advance job by one email if the delay has passed."""
    user_id = str(current_user["_id"])
    return json_safe(await tick_mail_job(db, user_id, job_id))

@router.post("/jobs/{job_id}/pause")
async def pause_job_route(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    success = await pause_job(db, user_id, job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause job")
    return {"message": "Job paused"}

@router.post("/jobs/{job_id}/resume")
async def resume_job_route(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    success = await resume_job(db, user_id, job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resume job")
    return {"message": "Job resumed"}

@router.post("/jobs/{job_id}/cancel")
async def cancel_job_route(job_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    success = await cancel_job(db, user_id, job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel job")
    return {"message": "Job cancelled"}

@router.post("/test")
async def test_single_mail(body: TestMailRequest, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    
    template = await db.mail_templates.find_one({"_id": body.template_id, "user_id": user_id})
    if not template:
        # Also check global/seeded templates
        template = await db.mail_templates.find_one({"_id": body.template_id, "is_global": True})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    smtp = await get_user_smtp_settings(db, user_id)
    if not smtp:
        raise HTTPException(status_code=400, detail="SMTP not configured")
        
    domain = smtp.get("smtp_user", "").split("@")[-1] if "@" in smtp.get("smtp_user", "") else "test.local"
        
    msg = await build_email_message(
        to_email=body.to_email,
        to_name=body.to_email.split("@")[0],
        subject=template["subject"],
        html_body=template["html_body"],
        from_name=smtp.get("from_name", ""),
        from_email=smtp.get("smtp_user", ""),
        reply_to=smtp.get("reply_to_email", ""),
        message_id_domain=domain,
        personalization_data={},
        attachments=[]
    )
    
    res = await send_single_email(smtp, msg, body.to_email)
    return res

@router.get("/logs")
async def get_mail_logs(
    page: int = 1, limit: int = 50, job_id: Optional[str] = None, 
    status: Optional[str] = None, search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    query = {"user_id": user_id}
    if job_id: query["job_id"] = job_id
    if status: query["status"] = status
    if search: 
        query["error_message"] = {"$regex": search, "$options": "i"}
        
    skip = (page - 1) * limit
    cursor = db.mail_logs.find(query).sort("sent_at", -1).skip(skip).limit(limit)
    logs = await cursor.to_list(length=limit)
    return json_safe(logs)
