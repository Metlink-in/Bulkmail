import secrets
import string
import bleach
import re
import bcrypt as _bcrypt
from datetime import datetime, timezone
from cryptography.fernet import Fernet

def generate_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for i in range(length))

def get_current_timestamp() -> datetime:
    return datetime.now(timezone.utc)

def json_safe(data):
    """Recursively convert ObjectIds and datetimes to JSON-serializable formats."""
    from bson import ObjectId
    if isinstance(data, list):
        return [json_safe(item) for item in data]
    if isinstance(data, dict):
        return {k: json_safe(v) for k, v in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    return data

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def encrypt_secret(value: str, key: str) -> str:
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()

def decrypt_secret(encrypted: str, key: str) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()

def sanitize_html(html: str) -> str:
    allowed_tags = ['p', 'br', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'img',
                    'span', 'div', 'strong', 'em', 'table', 'tr', 'td', 'th', 'thead', 'tbody']
    allowed_attributes = {
        '*': ['class', 'style'],
        'a': ['href', 'target', 'title'],
        'img': ['src', 'alt', 'width', 'height']
    }
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)

def validate_email_format(email: str) -> bool:
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return bool(re.match(pattern, email))
