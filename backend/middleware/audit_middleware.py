from fastapi import Request
from backend.utils.helpers import get_current_timestamp
from motor.motor_asyncio import AsyncIOMotorDatabase

async def log_audit(db: AsyncIOMotorDatabase, user_id: str, action: str, resource: str, detail: str, request: Request):
    ip_address = request.client.host if request.client else "unknown"
    
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
        
    import uuid
    audit_entry = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "detail": detail,
        "ip_address": ip_address,
        "timestamp": get_current_timestamp()
    }
    
    await db.audit_logs.insert_one(audit_entry)
