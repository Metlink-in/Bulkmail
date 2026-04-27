from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, Optional
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.services.reply_service import fetch_replies_for_user

router = APIRouter(tags=["replies"])

@router.post("/sync")
async def sync_replies(background_tasks: BackgroundTasks, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    background_tasks.add_task(fetch_replies_for_user, db, user_id)
    return {"message": "Sync started", "task_id": "background_sync"}

@router.get("")
async def get_replies(
    page: int = 1, limit: int = 50, is_read: Optional[bool] = None,
    job_id: Optional[str] = None, search: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    query = {"user_id": user_id, "is_deleted": {"$ne": True}}
    
    if is_read is not None: query["is_read"] = is_read
    if job_id: query["job_id"] = job_id
    if search:
        query["$or"] = [
            {"subject": {"$regex": search, "$options": "i"}},
            {"from_email": {"$regex": search, "$options": "i"}},
            {"body": {"$regex": search, "$options": "i"}}
        ]
        
    skip = (page - 1) * limit
    cursor = db.reply_inbox.find(query).sort("received_at", -1).skip(skip).limit(limit)
    replies = await cursor.to_list(length=limit)
    return replies

@router.get("/unread-count")
async def unread_count(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    count = await db.reply_inbox.count_documents({"user_id": user_id, "is_read": False, "is_deleted": {"$ne": True}})
    return {"count": count}

@router.get("/{reply_id}")
async def get_reply(reply_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.reply_inbox.find_one_and_update(
        {"_id": reply_id, "user_id": user_id},
        {"$set": {"is_read": True}},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="Reply not found")
    return res

@router.put("/{reply_id}/read")
async def mark_reply_read(reply_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.reply_inbox.update_one({"_id": reply_id, "user_id": user_id}, {"$set": {"is_read": True}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"message": "Marked as read"}

@router.post("/read-all")
async def mark_all_read(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    await db.reply_inbox.update_many(
        {"user_id": user_id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"message": "All marked as read"}

@router.delete("/{reply_id}")
async def delete_reply(reply_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.reply_inbox.update_one({"_id": reply_id, "user_id": user_id}, {"$set": {"is_deleted": True}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Reply not found")
    return {"message": "Reply deleted"}
