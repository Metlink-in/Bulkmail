import aiosmtplib
from email.message import EmailMessage
from core.database import get_db
from core.crypto import decrypt_value
from typing import Dict, Any

async def send_email(user_id: str, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
    db = get_db()
    user = await db.users.find_one({"_id": user_id})
    if not user or not user.get("smtp_config"):
        raise ValueError("SMTP configuration not found for user")
        
    smtp_config = user["smtp_config"]
    password = decrypt_value(smtp_config["password"])
    
    message = EmailMessage()
    message["From"] = smtp_config["username"]
    message["To"] = to_email
    message["Subject"] = subject
    
    if is_html:
        message.add_alternative(body, subtype="html")
    else:
        message.set_content(body)
        
    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_config["host"],
            port=smtp_config["port"],
            username=smtp_config["username"],
            password=password,
            use_tls=True if smtp_config["port"] == 465 else False,
            start_tls=True if smtp_config["port"] == 587 else False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
