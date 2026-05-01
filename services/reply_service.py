import imaplib
import email
from email.header import decode_header
import uuid
import asyncio
from datetime import datetime, timezone
from utils.helpers import decrypt_secret, get_current_timestamp
from config import settings

def decode_mime_words(s):
    if not s: return ""
    return u''.join(
        word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )

def fetch_imap_sync(host, port, user, password, last_date=None):
    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(user, password)
    mail.select("INBOX")
    
    # Simple search strategy: UNSEEN or SINCE
    search_criteria = 'ALL'
    if last_date:
        date_str = last_date.strftime("%d-%b-%Y")
        search_criteria = f'(SINCE "{date_str}")'
        
    status, messages = mail.search(None, search_criteria)
    if status != "OK":
        return []
        
    msg_ids = messages[0].split()
    parsed_emails = []
    
    for mid in msg_ids:
        res, msg_data = mail.fetch(mid, '(RFC822)')
        if res != 'OK': continue
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                in_reply_to = msg.get("In-Reply-To")
                if not in_reply_to:
                    continue # Skip if not a reply
                    
                subject = decode_mime_words(msg.get("Subject"))
                from_ = decode_mime_words(msg.get("From"))
                date_ = msg.get("Date")
                message_id = msg.get("Message-ID")
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode()
                                break
                            except: pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode()
                    except: pass
                    
                parsed_emails.append({
                    "from_email": from_,
                    "subject": subject,
                    "body": body,
                    "date": date_,
                    "message_id": message_id,
                    "in_reply_to": in_reply_to.strip("<>") if in_reply_to else None
                })
                
    mail.logout()
    return parsed_emails

async def fetch_replies_for_user(db, user_id: str):
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if not creds or not creds.get("imap_host"):
        return
        
    host = creds["imap_host"]
    port = creds.get("imap_port", 993)
    user = creds["imap_user"]
    password = decrypt_secret(creds["imap_password"], settings.ENCRYPTION_KEY)
    last_sync = creds.get("last_imap_sync")
    
    try:
        emails = await asyncio.to_thread(fetch_imap_sync, host, port, user, password, last_sync)
        
        for em in emails:
            # Check for dupes
            existing = await db.reply_inbox.find_one({"message_id": em["message_id"], "user_id": user_id})
            if existing: continue
            
            # Match to mail_logs
            orig_log = await db.mail_logs.find_one({"message_id": f"<{em['in_reply_to']}>", "user_id": user_id})
            job_id = orig_log["job_id"] if orig_log else None
            
            reply_doc = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "job_id": job_id,
                "from_email": em["from_email"],
                "subject": em["subject"],
                "body": em["body"],
                "message_id": em["message_id"],
                "in_reply_to": em["in_reply_to"],
                "received_at": get_current_timestamp(),
                "is_read": False,
                "is_deleted": False
            }
            await db.reply_inbox.insert_one(reply_doc)
            
        await db.user_credentials.update_one({"user_id": user_id}, {"$set": {"last_imap_sync": get_current_timestamp()}})
    except Exception as e:
        print(f"IMAP Fetch Error for {user_id}: {e}")
