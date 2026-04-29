from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.utils.helpers import sanitize_html, get_current_timestamp

router = APIRouter(tags=["template"])

class TemplateCreate(BaseModel):
    name: str
    subject: str
    html_body: str

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_body: Optional[str] = None

def strip_tags(html):
    import re
    return re.sub('<[^<]+?>', '', html)

@router.get("")
async def get_templates(page: int = 1, limit: int = 50, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    skip = (page - 1) * limit
    
    # Fetch both user templates and global templates
    query = {"$or": [{"user_id": user_id}, {"is_global": True}]}
    cursor = db.mail_templates.find(query).sort("is_global", -1).sort("updated_at", -1).skip(skip).limit(limit)
    templates = await cursor.to_list(length=limit)
    
    res = []
    for t in templates:
        t["id"] = str(t["_id"])
        t["preview_text"] = strip_tags(t.get("html_body", ""))[:100]
        # Keep html_body for the list if needed, but usually we don't for list views
        # In this app, templates.html needs the body for preview, so let's keep it for now
        t.pop("_id")
        res.append(t)
    return res

@router.post("")
async def create_template(body: TemplateCreate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    now = get_current_timestamp()
    
    clean_html = sanitize_html(body.html_body)
    
    t_id = str(uuid.uuid4())
    doc = {
        "_id": t_id,
        "user_id": user_id,
        "name": body.name,
        "subject": body.subject,
        "html_body": clean_html,
        "created_at": now,
        "updated_at": now
    }
    await db.mail_templates.insert_one(doc)
    doc["id"] = t_id
    doc.pop("_id")
    return doc

@router.get("/{template_id}")
async def get_template_details(template_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    # Allow users to view global templates or their own
    query = {"_id": template_id, "$or": [{"user_id": user_id}, {"is_global": True}]}
    t = await db.mail_templates.find_one(query)
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    t["id"] = str(t["_id"])
    t.pop("_id")
    return t

@router.put("/{template_id}")
async def update_template(template_id: str, body: TemplateUpdate, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    
    update_data = {"updated_at": get_current_timestamp()}
    if body.name is not None: update_data["name"] = body.name
    if body.subject is not None: update_data["subject"] = body.subject
    if body.html_body is not None: update_data["html_body"] = sanitize_html(body.html_body)
    
    res = await db.mail_templates.find_one_and_update(
        {"_id": template_id, "user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    if not res:
        raise HTTPException(status_code=404, detail="Template not found")
        
    res["id"] = str(res["_id"])
    res.pop("_id")
    return res

@router.delete("/{template_id}")
async def delete_template(template_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    res = await db.mail_templates.delete_one({"_id": template_id, "user_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted"}

@router.delete("/bulk/cleanup-auto")
async def cleanup_auto_templates(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    """Delete all auto-saved 'Campaign ...' templates for the current user."""
    user_id = str(current_user["_id"])
    res = await db.mail_templates.delete_many({
        "user_id": user_id,
        "name": {"$regex": r"^Campaign \d", "$options": "i"}
    })
    return {"message": f"Deleted {res.deleted_count} auto-saved campaign template(s)"}

@router.post("/{template_id}/duplicate")
async def duplicate_template(template_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    t = await db.mail_templates.find_one({"_id": template_id, "user_id": user_id})
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
        
    now = get_current_timestamp()
    new_id = str(uuid.uuid4())
    doc = {
        "_id": new_id,
        "user_id": user_id,
        "name": f"Copy of {t.get('name', 'Template')}",
        "subject": t.get("subject", ""),
        "html_body": t.get("html_body", ""),
        "created_at": now,
        "updated_at": now
    }
    await db.mail_templates.insert_one(doc)
    doc["id"] = new_id
    doc.pop("_id")
    return doc
