from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import uuid
from jose import jwt

from backend.database import get_db
from backend.middleware.auth_middleware import require_admin
from backend.utils.helpers import hash_password, get_current_timestamp, json_safe
from backend.config import settings

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
    from backend.middleware.auth_middleware import parse_object_id
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
    from backend.middleware.auth_middleware import parse_object_id
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
    from backend.middleware.auth_middleware import parse_object_id
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
    
    from backend.middleware.audit_middleware import log_audit
    admin_id = str(current_admin["_id"])
    await log_audit(db, admin_id, "user_crud_by_admin", "user", f"Deleted user {id_str}", request)
    
    return {"message": "User hard deleted"}

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from backend.middleware.auth_middleware import parse_object_id
    uid = parse_object_id(user_id)
    await db.users.update_one({"_id": uid}, {"$set": {"is_active": False}})
    return {"message": "User deactivated"}

@router.post("/users/{user_id}/activate")
async def activate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from backend.middleware.auth_middleware import parse_object_id
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
        from backend.middleware.auth_middleware import parse_object_id
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
        from backend.middleware.auth_middleware import parse_object_id
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
        from backend.utils.helpers import decrypt_secret
        from backend.config import settings
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
        from backend.middleware.auth_middleware import parse_object_id
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
            "user_name": u.get("name") if u else "Unknown",
            "user_email": u.get("email") if u else "Unknown",
            "template_name": t.get("name") if t else "Unknown",
            "sent": sent + failed,
            "total": total,
            "current_recipient": None,
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
        "emails_sent_last_minute": sent_1m,
        "emails_sent_last_hour": sent_1h,
        "errors_last_hour": err_1h,
        "active_users_online": active_users
    })

@router.get("/users/{user_id}/impersonate")
async def impersonate_user(user_id: str, current_admin: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    from backend.middleware.auth_middleware import parse_object_id
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
