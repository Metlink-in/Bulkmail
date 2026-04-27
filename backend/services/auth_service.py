from datetime import timedelta
from typing import Optional, Dict, Any
import uuid
from jose import jwt, JWTError
from fastapi import HTTPException, status
from backend.config import settings
from backend.utils.helpers import hash_password, verify_password, get_current_timestamp
from backend.models.user import UserCreate

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = get_current_timestamp() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = get_current_timestamp() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4()), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_by_email(db, email: str) -> Optional[Dict[str, Any]]:
    return await db.users.find_one({"email": email})

async def authenticate_user(db, email: str, password: str) -> Optional[Dict[str, Any]]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

async def register_user(db, user_create: UserCreate) -> Dict[str, Any]:
    existing = await get_user_by_email(db, user_create.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = hash_password(user_create.password)
    user_dict = {
        "_id": str(uuid.uuid4()),
        "email": user_create.email,
        "name": user_create.name,
        "org_name": user_create.org_name,
        "hashed_password": hashed_password,
        "role": "user",
        "is_active": True,
        "created_at": get_current_timestamp()
    }
    
    await db.users.insert_one(user_dict)
    return user_dict

async def revoke_token(db, jti: str):
    await db.revoked_tokens.insert_one({"jti": jti, "revoked_at": get_current_timestamp()})

async def is_token_revoked(db, jti: str) -> bool:
    token = await db.revoked_tokens.find_one({"jti": jti})
    return token is not None
