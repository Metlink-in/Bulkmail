import asyncio
import time
import uuid
import base64
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

from backend.utils.helpers import decrypt_secret
from backend.config import settings
from backend.services.validation_service import validate_email

MIN_DELAY_SECONDS = 60
DEFAULT_DELAY_SECONDS = 300
SPAM_WORDS = [
    "free", "winner", "urgent", "click here", "act now", "limited time",
    "guaranteed", "no risk", "earn money", "make money", "cash", "prize",
    "congratulations", "you've been selected", "double your", "earn per week",
    "exclusive deal", "get paid", "incredible deal", "no catch", "one hundred percent free",
    "promise you", "pure profit", "save big money", "unsolicited", "what are you waiting for",
    "while supplies last", "100% free", "call now", "deal of a lifetime"
]

async def get_user_smtp_settings(db, user_id: str) -> dict:
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds or not creds.get("smtp_host"):
        return {}
    
    password = creds.get("smtp_password")
    if password:
        creds["smtp_password_decrypted"] = decrypt_secret(password, settings.ENCRYPTION_KEY)
    
    return creds

async def build_email_message(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    from_name: str,
    from_email: str,
    reply_to: str,
    message_id_domain: str,
    personalization_data: dict,
    attachments: list
) -> MIMEMultipart:
    msg = MIMEMultipart('alternative')
    
    # Replace tokens
    tokens = {
        "{first_name}": personalization_data.get("first_name", to_name or "").split(" ")[0],
        "{last_name}": personalization_data.get("last_name", ""),
        "{company}": personalization_data.get("company", ""),
        "{custom_1}": personalization_data.get("custom_1", ""),
        "{custom_2}": personalization_data.get("custom_2", ""),
        "{custom_3}": personalization_data.get("custom_3", ""),
        "{custom_4}": personalization_data.get("custom_4", ""),
        "{custom_5}": personalization_data.get("custom_5", "")
    }
    
    s_sub = subject
    s_body = html_body
    for token, val in tokens.items():
        s_sub = s_sub.replace(token, str(val))
        s_body = s_body.replace(token, str(val))
        
    msg['Subject'] = s_sub
    msg['From'] = f"{from_name} <{from_email}>" if from_name else from_email
    msg['To'] = f"{to_name} <{to_email}>" if to_name else to_email
    if reply_to:
        msg['Reply-To'] = reply_to
        
    msg['Message-ID'] = f"<{uuid.uuid4()}@{message_id_domain}>"
    msg['X-Mailer'] = "BulkReach Pro Engine"
    
    # Text part
    import re
    text_body = re.sub('<[^<]+?>', '', s_body)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(s_body, 'html'))
    
    for att in attachments:
        filename = att.get('filename')
        content = att.get('content_base64')
        if filename and content:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(base64.b64decode(content))
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            
    return msg

def check_subject_for_spam(subject: str) -> dict:
    sub_lower = subject.lower()
    flagged = []
    for word in SPAM_WORDS:
        if word in sub_lower:
            flagged.append(word)
    score = len(flagged) * 10
    return {
        "has_spam": len(flagged) > 0,
        "flagged_words": flagged,
        "score": score
    }

async def send_single_email(smtp_settings: dict, message: MIMEMultipart, to_email: str) -> dict:
    host = smtp_settings.get("smtp_host")
    port = smtp_settings.get("smtp_port")
    user = smtp_settings.get("smtp_user")
    password = smtp_settings.get("smtp_password_decrypted")
    use_tls = smtp_settings.get("use_tls", False)
    use_ssl = smtp_settings.get("use_ssl", False)
    
    try:
        smtp_client = aiosmtplib.SMTP(hostname=host, port=port, use_tls=use_ssl, timeout=30)
        await smtp_client.connect()
        if use_tls:
            await smtp_client.starttls()
        await smtp_client.login(user, password)
        await smtp_client.send_message(message)
        await smtp_client.quit()
        return {"success": True, "message_id": message["Message-ID"], "error": None}
    except Exception as e:
        return {"success": False, "message_id": None, "error": str(e)}

async def process_mail_job(db, job_id: str):
    from backend.utils.helpers import get_current_timestamp
    
    job = await db.mail_jobs.find_one({"_id": job_id})
    if not job or job["status"] not in ["queued", "paused"]:
        return
        
    await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "running", "updated_at": get_current_timestamp()}})
    
    user_id = job["user_id"]
    smtp_settings = await get_user_smtp_settings(db, user_id)
    if not smtp_settings:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "failed", "error": "SMTP not configured"}})
        return
        
    template = await db.mail_templates.find_one({"_id": job.get("template_id")})
    if not template:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "failed", "error": "Template not found"}})
        return
        
    delay_seconds = job.get("interval_seconds", smtp_settings.get("email_delay_seconds", DEFAULT_DELAY_SECONDS))
    delay_seconds = max(MIN_DELAY_SECONDS, delay_seconds)
    
    daily_limit = job.get("daily_limit") or smtp_settings.get("daily_send_limit") or 500
    
    contacts = []
    contact_list_id = job.get("contact_list_id")
    if contact_list_id:
        c_list = await db.contacts.find({"list_id": contact_list_id}).to_list(None)
        contacts.extend(c_list)
        
    for cid in job.get("contact_ids", []):
        c = await db.contacts.find_one({"_id": cid})
        if c: contacts.append(c)
        
    # unique contacts
    contacts = {c["_id"]: c for c in contacts}.values()
    
    # Get already sent
    logs = await db.mail_logs.find({"job_id": job_id}).to_list(None)
    sent_contact_ids = {log["contact_id"] for log in logs if log["status"] == "sent"}
    
    domain = smtp_settings.get("smtp_user", "").split("@")[-1] if "@" in smtp_settings.get("smtp_user", "") else "bulkreach.local"
    
    from_name = job.get("from_name_override") or smtp_settings.get("from_name", "")
    from_email = smtp_settings.get("smtp_user", "")
    reply_to = job.get("reply_to_override") or smtp_settings.get("reply_to_email", "")
    
    # Simple rate limiting per day
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    for contact in contacts:
        # Check job status again
        current_job = await db.mail_jobs.find_one({"_id": job_id})
        if current_job["status"] != "running":
            break
            
        if contact["_id"] in sent_contact_ids:
            continue
            
        today_sent = await db.mail_logs.count_documents({
            "user_id": user_id, 
            "status": "sent",
            "sent_at": {"$gte": start_of_day}
        })
        if today_sent >= daily_limit:
            await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "paused", "updated_at": get_current_timestamp()}})
            break
            
        val = await validate_email(contact["email"])
        if val["status"] in ["invalid", "mx_fail"]:
            await db.mail_logs.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_id": job_id,
                "contact_id": contact["_id"],
                "sent_at": get_current_timestamp(),
                "status": "failed",
                "error_message": val["reason"]
            })
            continue
            
        personalization_data = contact.get("custom_fields", {})
        personalization_data["first_name"] = contact.get("name", "")
        personalization_data["company"] = contact.get("org", "")
        
        msg = await build_email_message(
            to_email=contact["email"],
            to_name=contact.get("name", ""),
            subject=template["subject"],
            html_body=template["html_body"],
            from_name=from_name,
            from_email=from_email,
            reply_to=reply_to,
            message_id_domain=domain,
            personalization_data=personalization_data,
            attachments=job.get("attachments_base64", [])
        )
        
        res = await send_single_email(smtp_settings, msg, contact["email"])
        
        await db.mail_logs.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "job_id": job_id,
            "contact_id": contact["_id"],
            "sent_at": get_current_timestamp(),
            "status": "sent" if res["success"] else "failed",
            "error_message": res["error"],
            "message_id": res["message_id"]
        })
        
        await db.audit_logs.insert_one({
            "user_id": user_id,
            "action": "send_campaign",
            "resource": job_id,
            "detail": f"Sent to {contact['email']}, success: {res['success']}",
            "ip_address": "system",
            "timestamp": get_current_timestamp()
        })
        
        await asyncio.sleep(delay_seconds)
        
    # Verify if complete
    logs = await db.mail_logs.count_documents({"job_id": job_id})
    if logs >= len(contacts):
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "completed", "completed_at": get_current_timestamp()}})

async def pause_job(db, user_id, job_id) -> bool:
    res = await db.mail_jobs.update_one({"_id": job_id, "user_id": user_id}, {"$set": {"status": "paused"}})
    return res.modified_count > 0

async def resume_job(db, user_id, job_id) -> bool:
    res = await db.mail_jobs.update_one({"_id": job_id, "user_id": user_id}, {"$set": {"status": "queued"}})
    return res.modified_count > 0

async def cancel_job(db, user_id, job_id) -> bool:
    res = await db.mail_jobs.update_one({"_id": job_id, "user_id": user_id}, {"$set": {"status": "cancelled"}})
    return res.modified_count > 0

async def get_job_status(db, user_id, job_id) -> dict:
    job = await db.mail_jobs.find_one({"_id": job_id, "user_id": user_id})
    if not job:
        return {}
        
    sent = await db.mail_logs.count_documents({"job_id": job_id, "status": "sent"})
    failed = await db.mail_logs.count_documents({"job_id": job_id, "status": "failed"})
    
    total = 0
    if job.get("contact_list_id"):
        total = await db.contacts.count_documents({"list_id": job.get("contact_list_id")})
    elif job.get("contact_ids"):
        total = len(job["contact_ids"])
        
    pct = (sent + failed) / total * 100 if total > 0 else 0
    
    started_at = job.get("updated_at")
    from backend.utils.helpers import get_current_timestamp
    elapsed = (get_current_timestamp() - started_at).total_seconds() if started_at else 0
    
    return {
        "status": job["status"],
        "sent_count": sent,
        "failed_count": failed,
        "total_count": total,
        "current_recipient": None,
        "progress_pct": pct,
        "started_at": started_at,
        "elapsed_seconds": int(elapsed)
    }
