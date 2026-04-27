from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import aiosmtplib
import imaplib
import ssl
import asyncio
import time
import google.generativeai as genai
import gspread

from backend.database import get_db
from backend.middleware.auth_middleware import require_user
from backend.utils.helpers import encrypt_secret, decrypt_secret
from backend.config import settings

router = APIRouter(tags=["settings"])

class SettingsBody(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: Optional[bool] = False
    use_ssl: Optional[bool] = False
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None
    fetch_interval_minutes: Optional[int] = 5
    gemini_api_key: Optional[str] = None
    from_name: Optional[str] = None
    reply_to_email: Optional[str] = None
    email_delay_seconds: Optional[int] = 300
    daily_send_limit: Optional[int] = 500
    warmup_mode: Optional[bool] = False
    unsubscribe_footer: Optional[str] = None
    google_sheets_api_key: Optional[str] = None
    default_sheet_id: Optional[str] = None

class SenderProfile(BaseModel):
    name: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    use_tls: bool = False
    use_ssl: bool = False
    imap_host: Optional[str] = None
    imap_port: Optional[int] = 993
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None
    from_name: str
    reply_to_email: str
    is_default: bool = False

@router.get("/profiles")
async def get_sender_profiles(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    cursor = db.user_credentials.find({"user_id": user_id})
    profiles = await cursor.to_list(length=100)
    for p in profiles:
        p["id"] = str(p.pop("_id"))
        p.pop("user_id", None)
        if p.get("smtp_password"): p["smtp_password"] = "••••••••"
        if p.get("imap_password"): p["imap_password"] = "••••••••"
    return profiles

@router.post("/profiles")
async def add_sender_profile(body: SenderProfile, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    data = body.dict()
    
    # Encrypt
    key = settings.ENCRYPTION_KEY
    data["smtp_password"] = encrypt_secret(data["smtp_password"], key)
    if data.get("imap_password"):
        data["imap_password"] = encrypt_secret(data["imap_password"], key)
    
    data["user_id"] = user_id
    
    if data["is_default"]:
        await db.user_credentials.update_many({"user_id": user_id}, {"$set": {"is_default": False}})
        
    result = await db.user_credentials.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Profile added"}

@router.put("/profiles/{profile_id}")
async def update_sender_profile(profile_id: str, body: SenderProfile, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    data = body.dict()
    
    from bson import ObjectId
    try:
        oid = ObjectId(profile_id)
    except:
        # handle UUID string if used previously, but let's assume ObjectId for new profiles
        oid = profile_id 

    # Handle password masking
    if data["smtp_password"] == "••••••••":
        data.pop("smtp_password")
    else:
        data["smtp_password"] = encrypt_secret(data["smtp_password"], settings.ENCRYPTION_KEY)
        
    if data.get("imap_password") == "••••••••":
        data.pop("imap_password")
    elif data.get("imap_password"):
        data["imap_password"] = encrypt_secret(data["imap_password"], settings.ENCRYPTION_KEY)

    if data.get("is_default"):
        await db.user_credentials.update_many({"user_id": user_id}, {"$set": {"is_default": False}})

    await db.user_credentials.update_one(
        {"_id": oid, "user_id": user_id},
        {"$set": data}
    )
    return {"message": "Profile updated"}

@router.delete("/profiles/{profile_id}")
async def delete_sender_profile(profile_id: str, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    from bson import ObjectId
    try: oid = ObjectId(profile_id)
    except: oid = profile_id
    
    await db.user_credentials.delete_one({"_id": oid, "user_id": user_id})
    return {"message": "Profile deleted"}

@router.get("")
async def get_settings(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    # Return general settings (like Gemini key, sheets key) which are shared
    creds = await db.user_credentials.find_one({"user_id": user_id, "is_default": True})
    if not creds:
        creds = await db.user_credentials.find_one({"user_id": user_id})
    
    if not creds:
        return {}
        
    creds.pop("_id", None)
    creds.pop("user_id", None)
    
    # Mask passwords
    if creds.get("smtp_password"):
        creds["smtp_password"] = "••••••••"
    if creds.get("imap_password"):
        creds["imap_password"] = "••••••••"
    if creds.get("gemini_api_key"):
        creds["gemini_api_key"] = "••••••••"
        
    return creds

@router.post("")
async def update_settings(body: SettingsBody, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    data = body.dict(exclude_unset=True)
    
    if data.get("email_delay_seconds") is not None and data["email_delay_seconds"] < 60:
        data["email_delay_seconds"] = 60
        
    # Encrypt secrets
    key = settings.ENCRYPTION_KEY
    if "smtp_password" in data and data["smtp_password"] != "••••••••":
        data["smtp_password"] = encrypt_secret(data["smtp_password"], key)
    elif "smtp_password" in data and data["smtp_password"] == "••••••••":
        data.pop("smtp_password")
        
    if "imap_password" in data and data["imap_password"] != "••••••••":
        data["imap_password"] = encrypt_secret(data["imap_password"], key)
    elif "imap_password" in data and data["imap_password"] == "••••••••":
        data.pop("imap_password")
        
    if "gemini_api_key" in data and data["gemini_api_key"] != "••••••••":
        data["gemini_api_key"] = encrypt_secret(data["gemini_api_key"], key)
    elif "gemini_api_key" in data and data["gemini_api_key"] == "••••••••":
        data.pop("gemini_api_key")
        
    await db.user_credentials.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )
    return {"message": "Settings updated successfully"}

@router.post("/smtp/test")
async def test_smtp(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds or not creds.get("smtp_host"):
        raise HTTPException(status_code=400, detail="SMTP settings not configured")
        
    host = creds["smtp_host"]
    port = creds["smtp_port"]
    user = creds["smtp_user"]
    password = decrypt_secret(creds["smtp_password"], settings.ENCRYPTION_KEY)
    use_tls = creds.get("use_tls", False)
    use_ssl = creds.get("use_ssl", False)
    
    start_time = time.time()
    try:
        smtp_client = aiosmtplib.SMTP(hostname=host, port=port, use_tls=use_ssl)
        await smtp_client.connect()
        if use_tls:
            await smtp_client.starttls()
        await smtp_client.login(user, password)
        await smtp_client.quit()
        latency = int((time.time() - start_time) * 1000)
        return {"success": True, "message": "SMTP connection successful", "latency_ms": latency}
    except Exception as e:
        return {"success": False, "message": str(e), "latency_ms": 0}

def test_imap_sync(host, port, user, password):
    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(user, password)
    status, mailboxes = mail.list()
    folder_count = len(mailboxes) if status == "OK" else 0
    mail.logout()
    return folder_count

@router.post("/imap/test")
async def test_imap(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds or not creds.get("imap_host"):
        raise HTTPException(status_code=400, detail="IMAP settings not configured")
        
    host = creds["imap_host"]
    port = creds["imap_port"] or 993
    user = creds["imap_user"]
    password = decrypt_secret(creds["imap_password"], settings.ENCRYPTION_KEY)
    
    try:
        folder_count = await asyncio.to_thread(test_imap_sync, host, port, user, password)
        return {"success": True, "message": "IMAP connection successful", "folder_count": folder_count}
    except Exception as e:
        return {"success": False, "message": str(e), "folder_count": 0}

@router.post("/ai/test")
async def test_ai(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    creds = await db.user_credentials.find_one({"user_id": user_id})
    api_key = creds.get("gemini_api_key") if creds else None
    
    if api_key:
        api_key = decrypt_secret(api_key, settings.ENCRYPTION_KEY)
    else:
        api_key = settings.GEMINI_API_KEY
        
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key not configured")
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello in one word")
        return {"success": True, "message": response.text.strip(), "model": "gemini-1.5-flash"}
    except Exception as e:
        return {"success": False, "message": str(e), "model": ""}

@router.post("/sheets/test")
async def test_sheets(body: SheetsTestBody, current_user: Dict[str, Any] = Depends(require_user)):
    try:
        gc = gspread.api_key(body.api_key)
        spreadsheet = gc.open_by_key(body.sheet_id)
        return {"success": True, "message": "Successfully accessed Google Sheet", "sheet_title": spreadsheet.title}
    except Exception as e:
        return {"success": False, "message": str(e), "sheet_title": ""}
