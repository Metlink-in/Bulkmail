from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from jose import jwt

from database import get_db
from middleware.auth_middleware import require_admin
from utils.helpers import hash_password, get_current_timestamp, json_safe
from config import settings

router = APIRouter(tags=["admin"])

class UserCreateAdmin(BaseModel):
    name: str
    email: EmailStr
    password: str
    org_name: Optional[str] = None
    role: str = "user"

class UserUpdateAdmin(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    org_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

class ResetPasswordAdmin(BaseModel):
    new_password: str

def get_db_id(doc):
    return str(doc.get("_id"))

# --- User Management ---

@router.get("/users")
async def get_users(
    page: int = 1, limit: int = 25, search: Optional[str] = None, is_active: Optional[bool] = None,
    current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)
):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    if is_active is not None:
        query["is_active"] = is_active
        
    skip = (page - 1) * limit
    cursor = db.users.find(query).sort("created_at", -1).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    result = []
    for u in users:
        u_id = get_db_id(u)
        total_sent = await db.mail_logs.count_documents({"user_id": u_id, "status": "sent"})
        active_jobs = await db.mail_jobs.count_documents({"user_id": u_id, "status": "running"})
        
        last_login_log = await db.audit_logs.find_one({"user_id": u_id, "action": "login"}, sort=[("timestamp", -1)])
        last_login = last_login_log["timestamp"] if last_login_log else None
        
        result.append({
            "id": u_id,
            "name": u.get("name"),
            "email": u.get("email"),
            "org_name": u.get("org_name"),
            "role": u.get("role"),
            "is_active": u.get("is_active"),
            "created_at": u.get("created_at"),
            "total_sent": total_sent,
            "active_jobs": active_jobs,
            "last_login": last_login
        })
    return json_safe(result)

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    u = await db.users.find_one({"_id": parse_object_id(user_id)})
    if not u:
        u = await db.users.find_one({"email": user_id})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
        
    u_id = get_db_id(u)
    total_sent = await db.mail_logs.count_documents({"user_id": u_id, "status": "sent"})
    total_jobs = await db.mail_jobs.count_documents({"user_id": u_id})
    
    u["id"] = u_id
    u.pop("_id")
    u.pop("hashed_password", None)
    
    return json_safe({
        "profile": u,
        "stats": {
            "total_sent": total_sent,
            "total_jobs": total_jobs
        }
    })

@router.post("/users")
async def create_user(body: UserCreateAdmin, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
        
    u_dict = {
        "email": body.email,
        "name": body.name,
        "org_name": body.org_name,
        "role": body.role,
        "is_active": True,
        "hashed_password": hash_password(body.password),
        "created_at": get_current_timestamp()
    }
    res = await db.users.insert_one(u_dict)
    u_dict["id"] = str(res.inserted_id)
    u_dict.pop("_id", None)
    u_dict.pop("hashed_password", None)
    return json_safe(u_dict)

@router.put("/users/{user_id}")
async def update_user(user_id: str, body: UserUpdateAdmin, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    
    update_data = body.dict(exclude_unset=True)
    if not update_data:
        return {"message": "No fields to update"}
        
    res = await db.users.find_one_and_update(
        {"_id": uid},
        {"$set": update_data},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    res["id"] = str(res["_id"])
    res.pop("_id", None)
    res.pop("hashed_password", None)
    return json_safe(res)

@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    u = await db.users.find_one({"_id": uid})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
        
    id_str = str(uid)
    await db.mail_jobs.delete_many({"user_id": id_str})
    await db.mail_logs.delete_many({"user_id": id_str})
    await db.mail_templates.delete_many({"user_id": id_str})
    await db.contact_lists.delete_many({"user_id": id_str})
    await db.contacts.delete_many({"user_id": id_str})
    await db.user_credentials.delete_many({"user_id": id_str})
    await db.reply_inbox.delete_many({"user_id": id_str})
    await db.scheduled_tasks.delete_many({"user_id": id_str})
    
    await db.users.delete_one({"_id": uid})
    
    from middleware.audit_middleware import log_audit
    admin_id = str(current_admin["_id"])
    await log_audit(db, admin_id, "user_crud_by_admin", "user", f"Deleted user {id_str}", request)
    
    return {"message": "User hard deleted"}

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    await db.users.update_one({"_id": uid}, {"$set": {"is_active": False}})
    return {"message": "User deactivated"}

@router.post("/users/{user_id}/activate")
async def activate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    await db.users.update_one({"_id": uid}, {"$set": {"is_active": True}})
    return {"message": "User activated"}


# --- System Oversight ---

@router.get("/stats")
async def get_system_stats(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    now = datetime.now(timezone.utc)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - timedelta(days=now.weekday())
    
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    new_today = await db.users.count_documents({"created_at": {"$gte": start_of_today}})
    new_week = await db.users.count_documents({"created_at": {"$gte": start_of_week}})
    
    total_emails = await db.mail_logs.count_documents({"status": "sent"})
    total_emails_today = await db.mail_logs.count_documents({"status": "sent", "sent_at": {"$gte": start_of_today}})
    
    active_jobs = await db.mail_jobs.count_documents({"status": "running"})
    failed_24h = await db.mail_logs.count_documents({"status": "failed", "sent_at": {"$gte": now - timedelta(days=1)}})
    
    active_schedules = await db.scheduled_tasks.count_documents({"is_active": True})
    
    hourly = [0] * 24
    pipeline = [
        {"$match": {"status": "sent", "sent_at": {"$gte": now - timedelta(days=1)}}},
        {"$project": {"h": {"$hour": "$sent_at"}}},
        {"$group": {"_id": "$h", "count": {"$sum": 1}}}
    ]
    hourly_agg = await db.mail_logs.aggregate(pipeline).to_list(24)
    for h in hourly_agg:
        if h["_id"] is not None and 0 <= h["_id"] <= 23:
            hourly[h["_id"]] = h["count"]
            
    top_pipeline = [
        {"$match": {"status": "sent", "sent_at": {"$gte": start_of_today}}},
        {"$group": {"_id": "$user_id", "sent_today": {"$sum": 1}}},
        {"$sort": {"sent_today": -1}},
        {"$limit": 5}
    ]
    top_users_agg = await db.mail_logs.aggregate(top_pipeline).to_list(5)
    
    top_users = []
    for tu in top_users_agg:
        from middleware.auth_middleware import parse_object_id
        u = await db.users.find_one({"_id": parse_object_id(tu["_id"])})
        if u:
            top_users.append({
                "name": u.get("name", "Unknown"),
                "email": u.get("email", "Unknown"),
                "sent_today": tu["sent_today"]
            })
            
    return json_safe({
        "total_users": total_users,
        "active_users": active_users,
        "new_users_today": new_today,
        "new_users_this_week": new_week,
        "total_emails_sent_all_time": total_emails,
        "total_emails_today": total_emails_today,
        "active_jobs_running": active_jobs,
        "failed_jobs_last_24h": failed_24h,
        "total_schedules_active": active_schedules,
        "emails_per_hour_last_24h": hourly,
        "top_active_users": top_users
    })

@router.get("/logs")
async def get_admin_logs(
    page: int = 1, limit: int = 50, user_id: Optional[str] = None, 
    action: Optional[str] = None, ip_address: Optional[str] = None,
    current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)
):
    query = {}
    if user_id: query["user_id"] = user_id
    if action: query["action"] = action
    if ip_address: query["ip_address"] = ip_address
    
    skip = (page - 1) * limit
    cursor = db.audit_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    logs = await cursor.to_list(limit)
    for log in logs:
        log["id"] = str(log.pop("_id"))
    return logs

@router.get("/mail-jobs")
async def get_admin_mail_jobs(
    page: int = 1, limit: int = 50, user_id: Optional[str] = None, status: Optional[str] = None,
    current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)
):
    query = {}
    if user_id: query["user_id"] = user_id
    if status: query["status"] = status
    
    skip = (page - 1) * limit
    cursor = db.mail_jobs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(limit)
    
    for j in jobs:
        j["id"] = str(j.pop("_id"))
        from middleware.auth_middleware import parse_object_id
        uid = parse_object_id(j["user_id"])
        u = await db.users.find_one({"_id": uid})
        if u:
            j["user_name"] = u.get("name")
            j["user_email"] = u.get("email")
            
    return json_safe(jobs)

@router.get("/mail-logs")
async def get_admin_mail_logs(
    page: int = 1, limit: int = 50, user_id: Optional[str] = None, status: Optional[str] = None,
    current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)
):
    query = {}
    if user_id: query["user_id"] = user_id
    if status: query["status"] = status
    
    skip = (page - 1) * limit
    cursor = db.mail_logs.find(query).sort("sent_at", -1).skip(skip).limit(limit)
    logs = await cursor.to_list(limit)
    for log in logs:
        log["id"] = str(log.pop("_id"))
    return logs


# --- Credentials Monitor ---

@router.get("/users/{user_id}/settings")
async def get_user_settings_admin(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds:
        return {}
        
    creds.pop("_id", None)
    creds.pop("user_id", None)
    
    if creds.get("smtp_password"): creds["smtp_password"] = "••••••••"
    if creds.get("imap_password"): creds["imap_password"] = "••••••••"
    
    g_key = creds.get("gemini_api_key")
    if g_key:
        from utils.helpers import decrypt_secret
        from config import settings
        dec = decrypt_secret(g_key, settings.ENCRYPTION_KEY)
        if len(dec) > 6:
            creds["gemini_api_key"] = "••••••••" + dec[-6:]
        else:
            creds["gemini_api_key"] = "••••••••"
            
    s_key = creds.get("google_sheets_api_key")
    if s_key:
        if len(s_key) > 6:
            creds["google_sheets_api_key"] = "••••••••" + s_key[-6:]
        else:
            creds["google_sheets_api_key"] = "••••••••"
            
    return json_safe(creds)


# --- Live Monitoring ---

@router.get("/live")
async def get_live_monitoring(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    now = datetime.now(timezone.utc)
    one_min_ago = now - timedelta(minutes=1)
    one_hour_ago = now - timedelta(hours=1)
    
    running_jobs_cursor = db.mail_jobs.find({"status": "running"})
    running_jobs_docs = await running_jobs_cursor.to_list(None)
    
    running_jobs = []
    for j in running_jobs_docs:
        from middleware.auth_middleware import parse_object_id
        uid = parse_object_id(j["user_id"])
        u = await db.users.find_one({"_id": uid})
        t = await db.mail_templates.find_one({"_id": j.get("template_id")})
        
        sent = await db.mail_logs.count_documents({"job_id": str(j["_id"]), "status": "sent"})
        failed = await db.mail_logs.count_documents({"job_id": str(j["_id"]), "status": "failed"})
        
        total = 0
        if j.get("contact_list_id"):
            total = await db.contacts.count_documents({"list_id": j.get("contact_list_id")})
        elif j.get("contact_ids"):
            total = len(j["contact_ids"])
            
        running_jobs.append({
            "job_id": str(j["_id"]),
            "user_id": j.get("user_id", ""),
            "user_name": u.get("name") if u else "Unknown",
            "user_email": u.get("email") if u else "Unknown",
            "template_name": t.get("name") if t else "Unknown",
            "status": j.get("status", "running"),
            "sent": sent,
            "failed": failed,
            "total": total,
            "started_at": j.get("updated_at")
        })
        
    queued_count = await db.mail_jobs.count_documents({"status": "queued"})
    sent_1m = await db.mail_logs.count_documents({"status": "sent", "sent_at": {"$gte": one_min_ago}})
    sent_1h = await db.mail_logs.count_documents({"status": "sent", "sent_at": {"$gte": one_hour_ago}})
    err_1h = await db.mail_logs.count_documents({"status": "failed", "sent_at": {"$gte": one_hour_ago}})
    
    ten_min_ago = now - timedelta(minutes=10)
    active_users = len(await db.audit_logs.distinct("user_id", {"timestamp": {"$gte": ten_min_ago}}))
    
    return json_safe({
        "timestamp": now.isoformat(),
        "running_jobs": running_jobs,
        "queued_jobs_count": queued_count,
        "emails_last_minute": sent_1m,
        "emails_last_hour": sent_1h,
        "errors_last_hour": err_1h,
        "active_users_last_5m": active_users
    })

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(user_id: str, body: ResetPasswordAdmin, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    if not body.new_password or len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    res = await db.users.find_one_and_update(
        {"_id": uid},
        {"$set": {"hashed_password": hash_password(body.new_password)}},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset successfully"}


@router.get("/users/{user_id}/smtp-profiles")
async def get_user_smtp_profiles(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from utils.helpers import decrypt_secret
    profiles = await db.user_credentials.find({"user_id": user_id, "name": {"$exists": True}}).to_list(100)
    result = []
    for p in profiles:
        p["id"] = str(p.pop("_id"))
        p.pop("user_id", None)
        if p.get("smtp_password"):
            try:
                p["smtp_password"] = decrypt_secret(p["smtp_password"], settings.ENCRYPTION_KEY)
            except Exception:
                p["smtp_password"] = ""
        if p.get("imap_password"):
            try:
                p["imap_password"] = decrypt_secret(p["imap_password"], settings.ENCRYPTION_KEY)
            except Exception:
                p["imap_password"] = ""
        result.append(p)
    return json_safe(result)


@router.post("/seed-templates")
async def seed_global_templates(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from templates_data import GLOBAL_TEMPLATES
    existing = await db.mail_templates.count_documents({"is_global": True})
    if existing > 0:
        return {"message": f"{existing} global templates already exist. Delete them in MongoDB first to re-seed.", "count": existing}

    now = get_current_timestamp()
    docs = []
    for t in GLOBAL_TEMPLATES:
        docs.append({
            "_id": str(uuid.uuid4()),
            "is_global": True,
            "user_id": "global",
            "name": t["name"],
            "subject": t["subject"],
            "html_body": t["html_body"].strip(),
            "created_at": now,
            "updated_at": now,
        })
    await db.mail_templates.insert_many(docs)
    return {"message": f"Seeded {len(docs)} global templates successfully.", "count": len(docs)}


@router.delete("/seed-templates")
async def delete_global_templates(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    res = await db.mail_templates.delete_many({"is_global": True})
    return {"message": f"Deleted {res.deleted_count} global templates.", "count": res.deleted_count}


@router.post("/templates/{template_id}/make-global")
async def make_template_global(template_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    """Mark any template as global so all users can see and use it."""
    res = await db.mail_templates.find_one_and_update(
        {"_id": template_id},
        {"$set": {"is_global": True, "updated_at": get_current_timestamp()}}
    )
    if not res:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template is now visible to all users"}


@router.post("/templates/{template_id}/make-private")
async def make_template_private(template_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    """Remove global flag — template becomes private to its owner again."""
    res = await db.mail_templates.find_one_and_update(
        {"_id": template_id},
        {"$unset": {"is_global": ""}, "$set": {"updated_at": get_current_timestamp()}}
    )
    if not res:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template is now private"}


@router.post("/templates/publish-all")
async def publish_all_admin_templates(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    """Mark ALL templates owned by the admin as global (visible to every user)."""
    admin_id = str(current_admin["_id"])
    res = await db.mail_templates.update_many(
        {"user_id": admin_id},
        {"$set": {"is_global": True, "updated_at": get_current_timestamp()}}
    )
    return {"message": f"Published {res.modified_count} template(s) as global", "count": res.modified_count}


@router.post("/jobs/{job_id}/force-cancel")
async def admin_force_cancel_job(job_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    res = await db.mail_jobs.find_one_and_update(
        {"_id": job_id, "status": {"$in": ["running", "queued", "paused"]}},
        {"$set": {"status": "cancelled", "updated_at": get_current_timestamp()}}
    )
    if not res:
        raise HTTPException(status_code=404, detail="Job not found or already completed/cancelled")
    return {"message": f"Job {job_id[:8]} force-cancelled"}


@router.post("/emergency-pause")
async def emergency_pause_all(current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    res = await db.mail_jobs.update_many(
        {"status": "running"},
        {"$set": {"status": "paused", "updated_at": get_current_timestamp()}}
    )
    return {"message": f"Paused {res.modified_count} running job(s)", "paused": res.modified_count}


@router.get("/users/{user_id}/impersonate")
async def impersonate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    u = await db.users.find_one({"_id": uid})
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
        
    u_id = get_db_id(u)
    
    token_data = {
        "sub": u_id,
        "role": u.get("role", "user"),
        "admin_impersonating": True
    }
    
    expire = get_current_timestamp() + timedelta(minutes=5)
    token_data.update({"exp": expire, "jti": str(uuid.uuid4()), "type": "access"})
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "impersonated_user": {
            "id": u_id,
            "email": u["email"],
            "name": u["name"]
        }
    }
