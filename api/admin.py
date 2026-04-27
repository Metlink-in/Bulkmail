from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db
from core.security import require_admin
from models.user import UserResponse
from typing import List

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(admin_user: dict = Depends(require_admin)):
    db = get_db()
    cursor = db.users.find()
    users = await cursor.to_list(length=100)
    
    result = []
    for user in users:
        result.append(UserResponse(
            id=user["_id"],
            email=user["email"],
            name=user["name"],
            role=user.get("role", "user"),
            is_active=user.get("is_active", True),
            has_smtp=user.get("smtp_config") is not None,
            has_ai=user.get("ai_config") is not None
        ))
    return result

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: str, admin_user: dict = Depends(require_admin)):
    db = get_db()
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot disable admin users")
        
    new_status = not user.get("is_active", True)
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {"is_active": new_status}}
    )
    
    return {"message": f"User {'activated' if new_status else 'deactivated'}"}

@router.get("/stats")
async def get_platform_stats(admin_user: dict = Depends(require_admin)):
    db = get_db()
    total_users = await db.users.count_documents({})
    total_campaigns = await db.campaigns.count_documents({})
    total_emails_sent = await db.recipients.count_documents({"status": "sent"})
    
    return {
        "total_users": total_users,
        "total_campaigns": total_campaigns,
        "total_emails_sent": total_emails_sent
    }
