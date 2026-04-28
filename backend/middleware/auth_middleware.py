from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from backend.database import get_db
from backend.services.auth_service import verify_token, is_token_revoked
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def parse_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except InvalidId:
        return id_str

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    jti: str = payload.get("jti")
    
    if not user_id or not jti:
        raise credentials_exception
        
    if await is_token_revoked(db, jti):
        raise credentials_exception
        
    user = await db.users.find_one({"_id": user_id})
    if not user:
        user = await db.users.find_one({"_id": parse_object_id(user_id)})
    if not user:
        user = await db.users.find_one({"email": user_id})
        
    if user is None:
        raise credentials_exception
        
    user["_id"] = str(user["_id"])
    return user

async def require_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return current_user
