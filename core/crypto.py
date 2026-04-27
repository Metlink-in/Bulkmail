from cryptography.fernet import Fernet
from core.config import settings

fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_value(value: str) -> str:
    if not value:
        return value
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return encrypted_value
    try:
        return fernet.decrypt(encrypted_value.encode()).decode()
    except Exception:
        return ""
