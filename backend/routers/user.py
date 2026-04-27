from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.models.user import UserResponse
from backend.utils.helpers import verify_password, hash_password
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["user"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    org_name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(require_user)):
    user_dict = dict(current_user)
    user_dict["id"] = str(user_dict.get("_id"))
    return UserResponse(**user_dict)

@router.put("/profile", response_model=UserResponse)
async def update_profile(body: ProfileUpdate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    
    update_data = {}
    if body.name is not None: update_data["name"] = body.name
    if body.org_name is not None: update_data["org_name"] = body.org_name
    
    if body.new_password:
        if not body.current_password:
            raise HTTPException(status_code=400, detail="Current password required to set new password")
        if not verify_password(body.current_password, current_user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect current password")
        if len(body.new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
        update_data["hashed_password"] = hash_password(body.new_password)
        
    if update_data:
        res = await db.users.find_one_and_update(
            {"_id": current_user["_id"]},
            {"$set": update_data},
            return_document=True
        )
    else:
        res = current_user
        
    user_dict = dict(res)
    user_dict["id"] = str(user_dict.get("_id"))
    return UserResponse(**user_dict)

@router.get("/stats")
async def get_user_stats(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    now = datetime.now(timezone.utc)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    
    total_sent = await db.mail_logs.count_documents({"user_id": user_id, "status": "sent"})
    sent_today = await db.mail_logs.count_documents({"user_id": user_id, "status": "sent", "sent_at": {"$gte": start_of_today}})
    
    active_schedules = await db.scheduled_tasks.count_documents({"user_id": user_id, "is_active": True})
    queued_jobs = await db.mail_jobs.count_documents({"user_id": user_id, "status": "queued"})
    failed_last_7 = await db.mail_logs.count_documents({"user_id": user_id, "status": "failed", "sent_at": {"$gte": seven_days_ago}})
    
    total_replies = await db.reply_inbox.count_documents({"user_id": user_id, "is_deleted": {"$ne": True}})
    reply_rate = (total_replies / total_sent * 100) if total_sent > 0 else 0.0
    
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$template_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    top_job = await db.mail_jobs.aggregate(pipeline).to_list(1)
    top_template = {"name": "None", "open_rate": 0}
    if top_job:
        t = await db.mail_templates.find_one({"_id": top_job[0]["_id"]})
        if t:
            top_template = {"name": t.get("name", "Unknown"), "open_rate": 0}
            
    return {
        "total_sent_all_time": total_sent,
        "sent_today": sent_today,
        "active_schedules": active_schedules,
        "queued_jobs": queued_jobs,
        "failed_last_7_days": failed_last_7,
        "reply_rate_percent": round(reply_rate, 2),
        "top_performing_template": top_template
    }

@router.get("/activity")
async def get_user_activity(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    cursor = db.audit_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(20)
    logs = await cursor.to_list(length=20)
    for log in logs:
        if "_id" in log:
            log["id"] = str(log["_id"])
            log.pop("_id")
    return logs
