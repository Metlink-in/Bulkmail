from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.services.contact_service import (
    parse_csv, import_from_sheets, save_contact_list, 
    get_contact_lists, get_contact_list, update_contact, delete_contact_list
)
from backend.services.validation_service import validate_email_list
import uuid
from datetime import datetime, timezone

router = APIRouter(tags=["contacts"])

class ContactListCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

class SheetsImportRequest(BaseModel):
    sheet_url: str
    range: str
    list_name: str

class ValidateEmailsRequest(BaseModel):
    emails: List[str]

@router.get("/lists")
async def list_contact_lists(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    lists = await get_contact_lists(db, user_id)
    return lists

@router.post("/lists")
async def create_contact_list(body: ContactListCreateRequest, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    result = await save_contact_list(db, user_id, body.name, [])
    if body.description:
        await db.contact_lists.update_one({"_id": result["_id"]}, {"$set": {"description": body.description}})
        result["description"] = body.description
    return result

@router.get("/{list_id}")
async def get_single_list(list_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    c_list = await get_contact_list(db, user_id, list_id)
    if not c_list:
        raise HTTPException(status_code=404, detail="Contact list not found")
        
    contacts = await db.contacts.find({"list_id": list_id, "user_id": user_id}).to_list(length=10000)
    c_list["contacts"] = contacts
    return c_list

@router.put("/{list_id}")
async def update_list_name(list_id: str, body: ContactListCreateRequest, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    c_list = await get_contact_list(db, user_id, list_id)
    if not c_list:
        raise HTTPException(status_code=404, detail="Contact list not found")
        
    await db.contact_lists.update_one(
        {"_id": list_id},
        {"$set": {"name": body.name, "description": body.description}}
    )
    return {"message": "Contact list updated"}

@router.delete("/{list_id}")
async def delete_list(list_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    success = await delete_contact_list(db, user_id, list_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact list not found")
    return {"message": "Contact list deleted"}

@router.post("/import/csv")
async def import_csv(
    list_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    content = await file.read()
    contacts = await parse_csv(content)
    
    result = await save_contact_list(db, user_id, list_name, contacts)
    
    valid_count = sum(1 for c in contacts if c["email_status"] == "valid")
    invalid_count = sum(1 for c in contacts if c["email_status"] == "invalid" or c["email_status"] == "mx_fail")
    risky_count = sum(1 for c in contacts if c["email_status"] == "risky")
    
    return {
        "list_id": result["_id"],
        "total_imported": len(contacts),
        "total_failed": 0,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "risky_count": risky_count,
        "errors": []
    }

@router.post("/import/sheets")
async def import_sheets(
    body: SheetsImportRequest,
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds or not creds.get("google_sheets_api_key"):
        raise HTTPException(status_code=400, detail="Google Sheets API key not configured in settings")
        
    api_key = creds["google_sheets_api_key"]
    contacts = await import_from_sheets(body.sheet_url, api_key, body.range)
    
    result = await save_contact_list(db, user_id, body.list_name, contacts)
    
    valid_count = sum(1 for c in contacts if c["email_status"] == "valid")
    invalid_count = sum(1 for c in contacts if c["email_status"] in ["invalid", "mx_fail"])
    risky_count = sum(1 for c in contacts if c["email_status"] == "risky")
    
    return {
        "list_id": result["_id"],
        "total_imported": len(contacts),
        "total_failed": 0,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "risky_count": risky_count,
        "errors": []
    }

@router.post("/{list_id}/contacts")
async def add_single_contact(list_id: str, data: Dict[str, Any], current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    
    # Check if list exists and belongs to user
    c_list = await db.contact_lists.find_one({"_id": list_id, "user_id": user_id})
    if not c_list:
        raise HTTPException(status_code=404, detail="Contact list not found")
        
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
        
    from backend.services.validation_service import validate_email
    validation = await validate_email(email)
    
    contact = {
        "_id": str(uuid.uuid4()),
        "list_id": list_id,
        "user_id": user_id,
        "email": email,
        "name": data.get("name"),
        "org": data.get("org"),
        "custom_fields": data.get("custom_fields", {}),
        "email_status": validation["status"],
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.contacts.insert_one(contact)
    return contact

@router.put("/{list_id}/contacts/{contact_id}")
async def update_single_contact(list_id: str, contact_id: str, data: Dict[str, Any], current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    
    if "email" in data:
        from backend.services.validation_service import validate_email
        validation = await validate_email(data["email"])
        data["email_status"] = validation["status"]
        
    updated = await update_contact(db, user_id, contact_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.post("/import/manual")
async def import_manual(
    list_name: str = Form(...),
    emails: str = Form(...),
    current_user: Dict[str, Any] = Depends(require_user),
    db = Depends(get_db)
):
    user_id = str(current_user["_id"])
    email_list = [e.strip() for e in emails.split('\n') if e.strip() and '@' in e]
    contacts = [{"email": e, "name": e.split('@')[0], "org": None, "custom_fields": {}, "email_status": "unknown"} for e in email_list]
    
    result = await save_contact_list(db, user_id, list_name, contacts)
    return {
        "list_id": result["_id"],
        "total_imported": len(contacts)
    }

@router.delete("/{list_id}/contacts/{contact_id}")
async def delete_single_contact(list_id: str, contact_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    result = await db.contacts.delete_one({"_id": contact_id, "list_id": list_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted"}

@router.post("/{list_id}/delete-bulk")
async def delete_bulk_contacts(list_id: str, body: Dict[str, List[str]], current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    contact_ids = body.get("contact_ids", [])
    result = await db.contacts.delete_many({"_id": {"$in": contact_ids}, "list_id": list_id, "user_id": user_id})
    return {"message": f"Deleted {result.deleted_count} contacts"}

@router.post("/validate")
async def validate_emails(body: ValidateEmailsRequest, current_user: Dict[str, Any] = Depends(require_user)):
    results = await validate_email_list(body.emails)
    return results
