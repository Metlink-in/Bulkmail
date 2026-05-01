from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import Dict, Any
from models.user import UserCreate, UserLogin, UserResponse
from database import get_db
from services.auth_service import (
    register_user, authenticate_user, create_access_token, create_refresh_token,
    verify_token, revoke_token
)
from middleware.auth_middleware import oauth2_scheme, require_user
from middleware.audit_middleware import log_audit
from motor.motor_asyncio import AsyncIOMotorDatabase
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["auth"])

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register")
async def register(
    request: Request,
    user_create: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if len(user_create.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
    user = await register_user(db, user_create)
    user_id = str(user.get("_id", user.get("id")))
    
    access_token = create_access_token(data={"sub": user_id, "role": user.get("role", "user")})
    refresh_token = create_refresh_token(data={"sub": user_id, "role": user.get("role", "user")})
    
    user["id"] = user_id
    
    await log_audit(db, user_id, "register", "auth", "User registered successfully", request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": UserResponse(**user)
    }

@router.post("/login")
@limiter.limit("100/minute")
async def login(
    request: Request,
    user_login: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user = await authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = str(user.get("_id", user.get("id")))
    
    access_token = create_access_token(data={"sub": user_id, "role": user.get("role", "user")})
    refresh_token = create_refresh_token(data={"sub": user_id, "role": user.get("role", "user")})
    
    user["id"] = user_id
    
    await log_audit(db, user_id, "login", "auth", "User logged in successfully", request)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": UserResponse(**user)
    }

@router.post("/refresh")
async def refresh(
    refresh_req: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        payload = verify_token(refresh_req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        # Generate new access token
        access_token = create_access_token(data={"sub": user_id, "role": role})
        return {"access_token": access_token}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(
    request: Request,
    refresh_req: RefreshRequest,
    token: str = Depends(oauth2_scheme),
    current_user: Dict[str, Any] = Depends(require_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        access_payload = verify_token(token)
        await revoke_token(db, access_payload.get("jti"))
        
        refresh_payload = verify_token(refresh_req.refresh_token)
        await revoke_token(db, refresh_payload.get("jti"))
        
        user_id = str(current_user.get("_id"))
        await log_audit(db, user_id, "logout", "auth", "User logged out", request)
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid tokens for logout")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(require_user)):
    user_dict = dict(current_user)
    user_dict["id"] = str(user_dict.get("_id"))
    return UserResponse(**user_dict)
