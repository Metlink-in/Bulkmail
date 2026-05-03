import asyncio
import os
import time
import uuid
import base64
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

from utils.helpers import decrypt_secret
from config import settings
from services.validation_service import validate_email

MIN_DELAY_SECONDS = 60
DEFAULT_DELAY_SECONDS = 300

# Values that look like unfilled placeholders — treat as empty
_PLACEHOLDER_VALUES = {
    "user", "users", "test", "name", "firstname", "first", "last", "lastname",
    "org", "company", "organisation", "organization", "email", "admin",
    "hello", "example", "sample", "demo", "unknown", "none", "null", "na", "n/a",
}

def _clean(val: str, fallback: str = "") -> str:
    """Return val unless it looks like a generic placeholder."""
    v = (val or "").strip()
    return fallback if v.lower() in _PLACEHOLDER_VALUES else v

SPAM_WORDS = [
    "free", "winner", "urgent", "click here", "act now", "limited time",
    "guaranteed", "no risk", "earn money", "make money", "cash", "prize",
    "congratulations", "you've been selected", "double your", "earn per week",
    "exclusive deal", "get paid", "incredible deal", "no catch", "one hundred percent free",
    "promise you", "pure profit", "save big money", "unsolicited", "what are you waiting for",
    "while supplies last", "100% free", "call now", "deal of a lifetime"
]

async def get_user_smtp_settings(db, user_id: str, profile_id: str = None) -> dict:
    if profile_id:
        from bson import ObjectId
        try: oid = ObjectId(profile_id)
        except: oid = profile_id
        creds = await db.user_credentials.find_one({"_id": oid, "user_id": user_id})
    else:
        creds = await db.user_credentials.find_one({"user_id": user_id, "is_default": True})
        if not creds:
            # Fallback to any profile if no default is set
            creds = await db.user_credentials.find_one({"user_id": user_id, "name": {"$exists": True}})
            
    if not creds:
        return {}
    
    # Merge with global settings from user_settings collection
    global_settings = await db.user_settings.find_one({"user_id": user_id})
    if global_settings:
        # Don't overwrite profile-specific SMTP/IMAP settings with global ones if they exist in global
        # but prioritize global settings for things like delay_seconds and daily_limit
        for key in ["email_delay_seconds", "daily_send_limit", "unsubscribe_footer", "gemini_api_key", "google_sheets_api_key"]:
            if global_settings.get(key) is not None:
                creds[key] = global_settings[key]
    
    password = creds.get("smtp_password")
    if password:
        try:
            creds["smtp_password_decrypted"] = decrypt_secret(password, settings.ENCRYPTION_KEY)
        except Exception:
            creds["smtp_password_decrypted"] = password
    
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
    # Use 'mixed' container when there are attachments; nest 'alternative' inside
    has_attachments = bool(attachments)
    if has_attachments:
        msg = MIMEMultipart('mixed')
        alt_part = MIMEMultipart('alternative')
    else:
        msg = MIMEMultipart('alternative')
        alt_part = msg
    
    # Replace tokens
    _first = personalization_data.get("first_name", to_name or "").split(" ")[0]
    _last  = personalization_data.get("last_name", "")
    _company = personalization_data.get("company", "")
    tokens = {
        "{first_name}": _first,
        "{last_name}":  _last,
        "{full_name}":  f"{_first} {_last}".strip() or _first,
        "{company}":    _company,
        "{org}":        _company,
        "{email}":      personalization_data.get("email", to_email),
        "{custom_1}":   personalization_data.get("custom_1", ""),
        "{custom_2}":   personalization_data.get("custom_2", ""),
        "{custom_3}":   personalization_data.get("custom_3", ""),
        "{custom_4}":   personalization_data.get("custom_4", ""),
        "{custom_5}":   personalization_data.get("custom_5", ""),
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
        
    from email.utils import formatdate
    msg['Date'] = formatdate(localtime=False)
    msg['MIME-Version'] = "1.0"
    msg['Message-ID'] = f"<{uuid.uuid4()}@{message_id_domain}>"
    
    # Plain-text part — clean whitespace after stripping tags
    import re
    text_body = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', s_body, flags=re.IGNORECASE)
    text_body = re.sub(r'<br\s*/?>', '\n', text_body, flags=re.IGNORECASE)
    text_body = re.sub(r'<p[^>]*>', '\n', text_body, flags=re.IGNORECASE)
    text_body = re.sub(r'<[^<]+?>', '', text_body)
    text_body = re.sub(r'[ \t]+', ' ', text_body)
    text_body = re.sub(r'\n{3,}', '\n\n', text_body).strip()
    alt_part.attach(MIMEText(text_body, 'plain', 'utf-8'))
    alt_part.attach(MIMEText(s_body, 'html', 'utf-8'))
    
    if has_attachments:
        msg.attach(alt_part)
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
        # For port 465, use_tls must be True in the constructor
        # For port 587, use_tls must be False and then call starttls()
        is_ssl = (port == 465 or use_ssl)
        
        smtp_client = aiosmtplib.SMTP(
            hostname=host, 
            port=port, 
            use_tls=is_ssl, 
            timeout=30
        )
        await smtp_client.connect()
        
        # Auto-detect STARTTLS: port 587 always requires it, or if use_tls is set
        if not is_ssl and (use_tls or port == 587):
            await smtp_client.starttls()
            
        await smtp_client.login(user, password)
        await smtp_client.send_message(message)
        await smtp_client.quit()
        return {"success": True, "message_id": message["Message-ID"], "error": None}
    except Exception as e:
        return {"success": False, "message_id": None, "error": str(e)}

async def process_mail_job(db, job_id: str):
    from utils.helpers import get_current_timestamp
    
    job = await db.mail_jobs.find_one({"_id": job_id})
    if not job or job["status"] not in ["queued", "paused"]:
        return
        
    await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "running", "updated_at": get_current_timestamp()}})
    
    user_id = job["user_id"]
    smtp_settings = await get_user_smtp_settings(db, user_id, job.get("sender_profile_id"))
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
        
    # unique contacts, convert to list for reuse and len()
    contacts = list({c["_id"]: c for c in contacts}.values())
    
    # Exit early if no contacts found for this job
    if not contacts:
        await db.mail_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "completed", "completed_at": get_current_timestamp(), "error": "No contacts found"}}
        )
        return
    
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
        # Warmup Mode logic: if enabled, max 20 emails/day first week, 50/day second week, then normal limits
        if smtp_settings.get("warmup_mode"):
            now = datetime.now(timezone.utc)
            created_at = smtp_settings.get("created_at") or now
            days_old = (now - created_at).days
            if days_old < 7:
                warmup_limit = 20
            elif days_old < 14:
                warmup_limit = 50
            else:
                warmup_limit = daily_limit
            
            effective_limit = min(daily_limit, warmup_limit)
        else:
            effective_limit = daily_limit

        if today_sent >= effective_limit:
            await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "paused", "updated_at": get_current_timestamp()}})
            break
            
        val = await validate_email(contact["email"])
        if val["status"] in ["invalid", "mx_fail"]:
            await db.mail_logs.insert_one({
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_id": job_id,
                "contact_id": contact["_id"],
                "email": contact["email"],
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
            "email": contact["email"],
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
    from utils.helpers import get_current_timestamp
    from datetime import timezone as _tz
    elapsed = 0
    if started_at:
        try:
            # Coerce naive datetimes from MongoDB to UTC-aware
            if hasattr(started_at, 'tzinfo') and started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=_tz.utc)
            elapsed = (get_current_timestamp() - started_at).total_seconds()
        except Exception:
            elapsed = 0
    
    return {
        "status": job["status"],
        "sent_count": sent,
        "failed_count": failed,
        "total_count": total,
        "current_recipient": job.get("current_recipient"),
        "progress_pct": pct,
        "started_at": started_at,
        "elapsed_seconds": int(elapsed),
        "next_send_at": job.get("next_send_at"),
    }


async def tick_mail_job(db, user_id: str, job_id: str) -> dict:
    """
    Serverless-compatible single-step processor.
    Called by the client poll loop — advances the job by one email each
    time the configured delay has passed. Safe to call as often as desired;
    it does nothing if it is not yet time to send the next email.
    """
    from utils.helpers import get_current_timestamp

    job = await db.mail_jobs.find_one({"_id": job_id, "user_id": user_id})
    if not job:
        return {}

    status = job.get("status")

    # Kick off a queued job on first tick
    if status == "queued":
        now = get_current_timestamp()
        await db.mail_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "running", "next_send_at": now, "updated_at": now}}
        )
        job = await db.mail_jobs.find_one({"_id": job_id})
        status = "running"

    if status != "running":
        return await get_job_status(db, user_id, job_id)

    # Not yet time to send next email
    now = get_current_timestamp()
    next_send_at = job.get("next_send_at")
    if next_send_at:
        if hasattr(next_send_at, 'tzinfo') and next_send_at.tzinfo is None:
            next_send_at = next_send_at.replace(tzinfo=timezone.utc)
        if next_send_at > now:
            return await get_job_status(db, user_id, job_id)

    smtp_settings = await get_user_smtp_settings(db, user_id, job.get("sender_profile_id"))
    if not smtp_settings:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "failed", "error": "SMTP not configured", "updated_at": now}})
        return await get_job_status(db, user_id, job_id)

    template = await db.mail_templates.find_one({"_id": job.get("template_id")})
    if not template:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "failed", "error": "Template not found", "updated_at": now}})
        return await get_job_status(db, user_id, job_id)

    delay_seconds = max(MIN_DELAY_SECONDS, job.get("interval_seconds") or smtp_settings.get("email_delay_seconds") or DEFAULT_DELAY_SECONDS)
    daily_limit = job.get("daily_limit") or smtp_settings.get("daily_send_limit") or 500

    # Load contacts
    contacts = []
    if job.get("contact_list_id"):
        contacts.extend(await db.contacts.find({"list_id": job["contact_list_id"]}).to_list(None))
    for cid in job.get("contact_ids", []):
        c = await db.contacts.find_one({"_id": cid})
        if c:
            contacts.append(c)
    contacts = list({c["_id"]: c for c in contacts}.values())

    if not contacts:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "completed", "completed_at": now}})
        return await get_job_status(db, user_id, job_id)

    logs = await db.mail_logs.find({"job_id": job_id}).to_list(None)
    processed_ids = {log["contact_id"] for log in logs}

    next_contact = next((c for c in contacts if c["_id"] not in processed_ids), None)
    if not next_contact:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "completed", "completed_at": now}})
        return await get_job_status(db, user_id, job_id)

    # Daily limit check
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_sent = await db.mail_logs.count_documents({"user_id": user_id, "status": "sent", "sent_at": {"$gte": start_of_day}})
    if today_sent >= daily_limit:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "paused", "updated_at": now}})
        return await get_job_status(db, user_id, job_id)

    from_email = smtp_settings.get("smtp_user", "")
    domain = from_email.split("@")[-1] if "@" in from_email else "bulkreach.local"
    _contact_name = _clean(next_contact.get("name", "")) or next_contact["email"].split("@")[0]
    _contact_org  = _clean(next_contact.get("org", ""))
    personalization_data = {
        **next_contact.get("custom_fields", {}),
        "first_name": _contact_name,
        "company":    _contact_org,
        "email":      next_contact["email"],
    }

    msg = await build_email_message(
        to_email=next_contact["email"],
        to_name=next_contact.get("name", ""),
        subject=template["subject"],
        html_body=template["html_body"],
        from_name=job.get("from_name_override") or smtp_settings.get("from_name", ""),
        from_email=from_email,
        reply_to=job.get("reply_to_override") or smtp_settings.get("reply_to_email", ""),
        message_id_domain=domain,
        personalization_data=personalization_data,
        attachments=job.get("attachments_base64", [])
    )

    res = await send_single_email(smtp_settings, msg, next_contact["email"])

    await db.mail_logs.insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "job_id": job_id,
        "contact_id": next_contact["_id"],
        "email": next_contact["email"],
        "sent_at": now,
        "status": "sent" if res["success"] else "failed",
        "error_message": res["error"],
        "message_id": res["message_id"]
    })

    update = {
        "next_send_at": now + timedelta(seconds=delay_seconds),
        "current_recipient": next_contact["email"],
        "updated_at": now,
    }

    total = len(contacts)
    done = await db.mail_logs.count_documents({"job_id": job_id})
    if done >= total:
        update["status"] = "completed"
        update["completed_at"] = now
    await db.mail_jobs.update_one({"_id": job_id}, {"$set": update})

    return await get_job_status(db, user_id, job_id)


# ── Custom Outreach (inline recipients, no template) ──────────────────────────

async def _outreach_status(db, job_id: str, job: dict) -> dict:
    sent   = await db.mail_logs.count_documents({"job_id": job_id, "status": "sent"})
    failed = await db.mail_logs.count_documents({"job_id": job_id, "status": "failed"})
    total  = len(job.get("inline_recipients", []))
    pct    = round((sent + failed) / total * 100, 1) if total > 0 else 0
    return {
        "status":            job.get("status"),
        "sent_count":        sent,
        "failed_count":      failed,
        "total_count":       total,
        "current_recipient": job.get("current_recipient"),
        "progress_pct":      pct,
        "next_send_at":      job.get("next_send_at"),
    }


async def tick_outreach_job(db, user_id: str, job_id: str) -> dict:
    """Serverless-compatible single-step processor for Custom Outreach jobs."""
    from utils.helpers import get_current_timestamp

    job = await db.mail_jobs.find_one({"_id": job_id, "user_id": user_id})
    if not job:
        return {}

    status = job.get("status")
    if status == "queued":
        now = get_current_timestamp()
        await db.mail_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "running", "next_send_at": now, "updated_at": now}}
        )
        job = await db.mail_jobs.find_one({"_id": job_id})
        status = "running"

    if status != "running":
        return await _outreach_status(db, job_id, job)

    now = get_current_timestamp()
    next_send_at = job.get("next_send_at")
    if next_send_at:
        if hasattr(next_send_at, "tzinfo") and next_send_at.tzinfo is None:
            next_send_at = next_send_at.replace(tzinfo=timezone.utc)
        if next_send_at > now:
            return await _outreach_status(db, job_id, job)

    smtp_settings = await get_user_smtp_settings(db, user_id, job.get("sender_profile_id"))
    if not smtp_settings:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "failed", "error": "SMTP not configured", "updated_at": now}})
        return await _outreach_status(db, job_id, await db.mail_jobs.find_one({"_id": job_id}))

    recipients = job.get("inline_recipients", [])
    if not recipients:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "completed", "completed_at": now}})
        return await _outreach_status(db, job_id, await db.mail_jobs.find_one({"_id": job_id}))

    logs = await db.mail_logs.find({"job_id": job_id}).to_list(None)
    processed_emails = {log["email"] for log in logs}

    next_r = next((r for r in recipients if r["email"] not in processed_emails), None)
    if not next_r:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "completed", "completed_at": now}})
        return await _outreach_status(db, job_id, await db.mail_jobs.find_one({"_id": job_id}))

    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_limit  = job.get("daily_limit") or smtp_settings.get("daily_send_limit") or 500
    today_sent   = await db.mail_logs.count_documents({"user_id": user_id, "status": "sent", "sent_at": {"$gte": start_of_day}})
    if today_sent >= daily_limit:
        await db.mail_jobs.update_one({"_id": job_id}, {"$set": {"status": "paused", "updated_at": now}})
        return await _outreach_status(db, job_id, await db.mail_jobs.find_one({"_id": job_id}))

    delay_seconds = max(MIN_DELAY_SECONDS, job.get("interval_seconds") or smtp_settings.get("email_delay_seconds") or DEFAULT_DELAY_SECONDS)
    from_email    = smtp_settings.get("smtp_user", "")
    domain        = from_email.split("@")[-1] if "@" in from_email else "bulkreach.local"

    first_name = _clean(next_r.get("first_name", "")) or next_r["email"].split("@")[0]
    last_name  = _clean(next_r.get("last_name", ""))
    company    = _clean(next_r.get("company", ""))
    full_name  = f"{first_name} {last_name}".strip()

    personalization_data = {
        "first_name": first_name,
        "last_name":  last_name,
        "full_name":  full_name,
        "company":    company,
        "email":      next_r["email"],
        "custom_1":   next_r.get("custom_1", ""),
        "custom_2":   next_r.get("custom_2", ""),
        "custom_3":   next_r.get("custom_3", ""),
    }

    msg = await build_email_message(
        to_email=next_r["email"],
        to_name=full_name or first_name,
        subject=job["subject"],
        html_body=job["html_body"],
        from_name=smtp_settings.get("from_name", ""),
        from_email=from_email,
        reply_to=smtp_settings.get("reply_to_email", ""),
        message_id_domain=domain,
        personalization_data=personalization_data,
        attachments=[],
    )

    res = await send_single_email(smtp_settings, msg, next_r["email"])

    await db.mail_logs.insert_one({
        "_id":           str(uuid.uuid4()),
        "user_id":       user_id,
        "job_id":        job_id,
        "contact_id":    next_r["email"],
        "email":         next_r["email"],
        "sent_at":       now,
        "status":        "sent" if res["success"] else "failed",
        "error_message": res.get("error"),
        "message_id":    res.get("message_id"),
    })

    done  = await db.mail_logs.count_documents({"job_id": job_id})
    total = len(recipients)
    update = {
        "next_send_at":      now + timedelta(seconds=delay_seconds),
        "current_recipient": next_r["email"],
        "updated_at":        now,
    }
    if done >= total:
        update["status"]       = "completed"
        update["completed_at"] = now

    await db.mail_jobs.update_one({"_id": job_id}, {"$set": update})
    return await _outreach_status(db, job_id, await db.mail_jobs.find_one({"_id": job_id}))
