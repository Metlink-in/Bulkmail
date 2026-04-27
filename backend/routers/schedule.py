from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.utils.helpers import get_current_timestamp
from backend.services.scheduler_service import schedule_recurring, cancel_scheduled_job

router = APIRouter(tags=["schedule"])

class ScheduledTaskCreate(BaseModel):
    name: str
    template_id: str
    contact_list_id: str
    recurrence_type: str # "once"|"daily"|"weekly"|"custom"
    cron_expression: Optional[str] = None
    run_at: Optional[datetime] = None
    time_of_day: Optional[str] = None # HH:MM
    day_of_week: Optional[int] = None # 0-6

class ScheduledTaskUpdate(BaseModel):
    template_id: Optional[str] = None
    contact_list_id: Optional[str] = None
    cron_expression: Optional[str] = None
    time_of_day: Optional[str] = None
    day_of_week: Optional[int] = None
    is_active: Optional[bool] = None

def build_cron(data: ScheduledTaskCreate | ScheduledTaskUpdate, current_cron: str = None) -> str:
    if getattr(data, 'recurrence_type', None) == 'custom':
        return data.cron_expression
    
    tod = getattr(data, 'time_of_day', None)
    dow = getattr(data, 'day_of_week', None)
    
    if getattr(data, 'recurrence_type', None) == 'daily' and tod:
        h, m = tod.split(":")
        return f"{m} {h} * * *"
        
    if getattr(data, 'recurrence_type', None) == 'weekly' and tod and dow is not None:
        h, m = tod.split(":")
        return f"{m} {h} * * {dow}"
        
    return current_cron

@router.get("")
async def get_scheduled_tasks(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    cursor = db.scheduled_tasks.find({"user_id": user_id}).sort("next_run", 1)
    return await cursor.to_list(None)

@router.post("")
async def create_scheduled_task(body: ScheduledTaskCreate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    t_id = str(uuid.uuid4())
    now = get_current_timestamp()
    
    cron = build_cron(body)
    
    doc = {
        "_id": t_id,
        "user_id": user_id,
        "name": body.name,
        "template_id": body.template_id,
        "contact_list_id": body.contact_list_id,
        "recurrence_type": body.recurrence_type,
        "cron_expression": cron,
        "run_at": body.run_at,
        "is_active": True,
        "next_run": body.run_at if body.recurrence_type == "once" else None,
        "created_at": now,
        "updated_at": now
    }
    
    await db.scheduled_tasks.insert_one(doc)
    
    if cron:
        await schedule_recurring(db, t_id, cron)
    
    return doc

@router.get("/{task_id}")
async def get_scheduled_task(task_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    t = await db.scheduled_tasks.find_one({"_id": task_id, "user_id": user_id})
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
        
    recent_jobs = await db.mail_jobs.find({"user_id": user_id, "scheduled_at": {"$exists": True}}).sort("created_at", -1).limit(10).to_list(None)
    t["recent_executions"] = recent_jobs
    return t

@router.put("/{task_id}")
async def update_scheduled_task(task_id: str, body: ScheduledTaskUpdate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    task = await db.scheduled_tasks.find_one({"_id": task_id, "user_id": user_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = {"updated_at": get_current_timestamp()}
    if body.template_id is not None: update_data["template_id"] = body.template_id
    if body.contact_list_id is not None: update_data["contact_list_id"] = body.contact_list_id
    if body.is_active is not None: update_data["is_active"] = body.is_active
    
    cron = build_cron(body, task.get("cron_expression"))
    if cron: update_data["cron_expression"] = cron
    
    res = await db.scheduled_tasks.find_one_and_update(
        {"_id": task_id, "user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    
    if cron and res.get("is_active"):
        await cancel_scheduled_job(task_id)
        await schedule_recurring(db, task_id, cron)
        
    return res

@router.delete("/{task_id}")
async def delete_scheduled_task(task_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.scheduled_tasks.delete_one({"_id": task_id, "user_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
        
    await cancel_scheduled_job(task_id)
    return {"message": "Scheduled task deleted"}

@router.post("/{task_id}/pause")
async def pause_scheduled_task(task_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.scheduled_tasks.find_one_and_update(
        {"_id": task_id, "user_id": user_id},
        {"$set": {"is_active": False}},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="Task not found")
    await cancel_scheduled_job(task_id)
    return {"message": "Scheduled task paused"}

@router.post("/{task_id}/resume")
async def resume_scheduled_task(task_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.scheduled_tasks.find_one_and_update(
        {"_id": task_id, "user_id": user_id},
        {"$set": {"is_active": True}},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if res.get("cron_expression"):
        await schedule_recurring(db, task_id, res["cron_expression"])
    return {"message": "Scheduled task resumed"}
