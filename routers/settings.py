from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import aiosmtplib
import imaplib
import ssl
import asyncio
import time

from database import get_db
from middleware.auth_middleware import require_user, require_admin
from utils.helpers import encrypt_secret, decrypt_secret, json_safe
from config import settings

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

class SheetsTestBody(BaseModel):
    api_key: str
    sheet_id: str

class SmtpTestRequest(BaseModel):
    profile_id: Optional[str] = None
    to_email: Optional[str] = None   # if set, sends a real test email

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
    # Filter for documents that have a 'name' field, which identifies them as Sender Profiles
    cursor = db.user_credentials.find({"user_id": user_id, "name": {"$exists": True}})
    profiles = await cursor.to_list(length=100)
    for p in profiles:
        p["id"] = str(p.pop("_id"))
        p.pop("user_id", None)
        if p.get("smtp_password"): p["smtp_password"] = "••••••••"
        if p.get("imap_password"): p["imap_password"] = "••••••••"
    return json_safe(profiles)

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
    return json_safe({"id": str(result.inserted_id), "message": "Profile added"})

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

@router.get("/env-smtp")
async def get_env_smtp(current_user: Dict[str, Any] = Depends(require_admin)):
    """Return what SMTP vars are configured in .env (password masked)."""
    configured = bool(settings.SMTP_HOST and settings.SMTP_USER)
    return {
        "configured": configured,
        "smtp_host": settings.SMTP_HOST or "",
        "smtp_port": settings.SMTP_PORT or 587,
        "smtp_user": settings.SMTP_USER or "",
        "smtp_password": "••••••••" if settings.SMTP_PASSWORD else "",
        "use_tls": settings.SMTP_USE_TLS,
        "use_ssl": settings.SMTP_USE_SSL,
        "from_name": settings.SMTP_FROM_NAME or "",
        "reply_to_email": settings.SMTP_REPLY_TO or "",
    }

@router.post("/profiles/from-env")
async def apply_env_smtp(current_user: Dict[str, Any] = Depends(require_admin), db = Depends(get_db)):
    """Create or update the user's 'Default (.env)' sender profile from env vars."""
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise HTTPException(status_code=400, detail="SMTP_HOST, SMTP_USER and SMTP_PASSWORD must all be set in .env")

    user_id = str(current_user["_id"])
    key = settings.ENCRYPTION_KEY
    enc_password = encrypt_secret(settings.SMTP_PASSWORD, key)

    data = {
        "name": "Default (.env)",
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT or 587,
        "smtp_user": settings.SMTP_USER,
        "smtp_password": enc_password,
        "use_tls": settings.SMTP_USE_TLS,
        "use_ssl": settings.SMTP_USE_SSL,
        "from_name": settings.SMTP_FROM_NAME or settings.SMTP_USER,
        "reply_to_email": settings.SMTP_REPLY_TO or settings.SMTP_USER,
        "imap_host": None,
        "imap_port": 993,
        "imap_user": None,
        "imap_password": None,
        "user_id": user_id,
        "is_default": True,
    }

    # Clear existing default
    await db.user_credentials.update_many({"user_id": user_id}, {"$set": {"is_default": False}})

    # Upsert by name so clicking the button twice doesn't create duplicates
    existing = await db.user_credentials.find_one({"user_id": user_id, "name": "Default (.env)"})
    if existing:
        await db.user_credentials.update_one({"_id": existing["_id"]}, {"$set": data})
        return {"message": "Default (.env) profile updated from environment variables"}
    else:
        await db.user_credentials.insert_one(data)
        return {"message": "Default (.env) profile created from environment variables"}

@router.get("")
async def get_settings(current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    # Use a separate collection for global app settings to avoid conflict with sender profiles
    creds = await db.user_settings.find_one({"user_id": user_id})
    
    if not creds:
        return {}
        
    creds.pop("_id", None)
    creds.pop("user_id", None)
    
    # Mask passwords/keys
    for k in ["smtp_password", "imap_password", "gemini_api_key", "google_sheets_api_key"]:
        if creds.get(k):
            creds[k] = "••••••••"
            
    return json_safe(creds)

@router.post("")
async def update_settings(body: SettingsBody, current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    data = body.dict(exclude_unset=True)
    
    if data.get("email_delay_seconds") is not None and data["email_delay_seconds"] < 60:
        data["email_delay_seconds"] = 60
        
    # Encrypt secrets
    key = settings.ENCRYPTION_KEY
    for k in ["smtp_password", "imap_password", "gemini_api_key", "google_sheets_api_key"]:
        if k in data:
            if data[k] == "••••••••":
                data.pop(k)
            else:
                data[k] = encrypt_secret(data[k], key)
        
    await db.user_settings.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )
    return {"message": "Settings updated successfully"}

@router.post("/smtp/test")
async def test_smtp(body: SmtpTestRequest = SmtpTestRequest(), current_user: Dict[str, Any] = Depends(require_user), db = Depends(get_db)):
    user_id = str(current_user["_id"])
    from bson import ObjectId

    if body.profile_id:
        # Test a specific profile by id
        try:
            oid = ObjectId(body.profile_id)
        except Exception:
            oid = body.profile_id
        creds = await db.user_credentials.find_one({"_id": oid, "user_id": user_id})
    else:
        creds = await db.user_credentials.find_one({"user_id": user_id, "is_default": True, "name": {"$exists": True}})
        if not creds:
            creds = await db.user_credentials.find_one({"user_id": user_id, "name": {"$exists": True}})

    if not creds or not creds.get("smtp_host"):
        raise HTTPException(status_code=400, detail="SMTP settings not configured. Add a Sender Profile first.")
        
    host = creds["smtp_host"]
    port = creds["smtp_port"]
    user = creds["smtp_user"]
    try:
        password = decrypt_secret(creds["smtp_password"], settings.ENCRYPTION_KEY)
    except Exception:
        password = creds["smtp_password"]  # Fallback: use as-is if not encrypted
    use_tls = creds.get("use_tls", False)
    use_ssl = creds.get("use_ssl", False)
    
    start_time = time.time()
    try:
        is_ssl = (port == 465 or use_ssl)
        needs_starttls = (not is_ssl) and (use_tls or port == 587)
        smtp_client = aiosmtplib.SMTP(hostname=host, port=port, use_tls=is_ssl, timeout=30)
        await smtp_client.connect()
        if needs_starttls:
            await smtp_client.starttls()
        await smtp_client.login(user, password)

        # Send a real test email if to_email was supplied
        if body.to_email:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "✅ BulkReach Pro — SMTP Test"
            msg["From"] = f"{creds.get('from_name', user)} <{user}>"
            msg["To"] = body.to_email
            html = (
                "<div style='font-family:sans-serif;max-width:480px'>"
                "<h2 style='color:#6366f1'>SMTP test successful ✅</h2>"
                f"<p>Your SMTP profile <strong>{creds.get('name','')}</strong> is working correctly.</p>"
                f"<p style='color:#6b7280;font-size:13px'>Sent via {host}:{port}</p>"
                "</div>"
            )
            msg.attach(MIMEText(html, "html"))
            await smtp_client.send_message(msg)
            await smtp_client.quit()
            latency = int((time.time() - start_time) * 1000)
            return {"success": True, "message": f"Test email sent to {body.to_email} via {host}:{port}", "latency_ms": latency}

        await smtp_client.quit()
        latency = int((time.time() - start_time) * 1000)
        return {"success": True, "message": f"SMTP connection to {host}:{port} successful", "latency_ms": latency}
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
    import httpx
    user_id = str(current_user["_id"])
    creds = await db.user_settings.find_one({"user_id": user_id})
    api_key = creds.get("gemini_api_key") if creds else None

    if api_key:
        api_key = decrypt_secret(api_key, settings.ENCRYPTION_KEY)
    else:
        api_key = settings.GEMINI_API_KEY

    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key not configured")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "Say hello in one word"}]}]}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return {"success": True, "message": text, "model": "gemini-1.5-flash"}
    except Exception as e:
        return {"success": False, "message": str(e), "model": ""}

@router.post("/sheets/test")
async def test_sheets(body: SheetsTestBody, current_user: Dict[str, Any] = Depends(require_user)):
    try:
        import gspread
        gc = gspread.api_key(body.api_key)
        spreadsheet = gc.open_by_key(body.sheet_id)
        return {"success": True, "message": "Successfully accessed Google Sheet", "sheet_title": spreadsheet.title}
    except Exception as e:
        return {"success": False, "message": str(e), "sheet_title": ""}
