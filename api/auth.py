from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token, get_current_user
from core.crypto import encrypt_value, decrypt_value
from models.user import UserCreate, UserResponse, SmtpConfig, AiConfig, Token
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = get_db()
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)
    
    # First user becomes admin
    count = await db.users.count_documents({})
    role = "admin" if count == 0 else "user"
    
    new_user = {
        "_id": user_id,
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "role": role,
        "is_active": True,
        "smtp_config": None,
        "ai_config": None
    }
    
    await db.users.insert_one(new_user)
    
    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        role=role,
        is_active=True
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    is_admin = user.get("role") == "admin"
    access_token = create_access_token(
        data={"sub": user["_id"], "role": user.get("role", "user")},
        is_admin=is_admin
    )
    return {"access_token": access_token, "token_type": "bearer", "is_admin": is_admin}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserResponse(
        id=user["_id"],
        email=user["email"],
        name=user["name"],
        role=user.get("role", "user"),
        is_active=user.get("is_active", True),
        has_smtp=user.get("smtp_config") is not None,
        has_ai=user.get("ai_config") is not None
    )

@router.post("/settings/smtp")
async def update_smtp_settings(config: SmtpConfig, current_user: dict = Depends(get_current_user)):
    db = get_db()
    encrypted_password = encrypt_value(config.password)
    
    smtp_data = {
        "host": config.host,
        "port": config.port,
        "username": config.username,
        "password": encrypted_password
    }
    
    await db.users.update_one(
        {"_id": current_user["user_id"]},
        {"$set": {"smtp_config": smtp_data}}
    )
    return {"message": "SMTP configuration updated successfully"}

@router.post("/settings/ai")
async def update_ai_settings(config: AiConfig, current_user: dict = Depends(get_current_user)):
    db = get_db()
    encrypted_key = encrypt_value(config.gemini_api_key)
    
    ai_data = {
        "gemini_api_key": encrypted_key
    }
    
    await db.users.update_one(
        {"_id": current_user["user_id"]},
        {"$set": {"ai_config": ai_data}}
    )
    return {"message": "AI configuration updated successfully"}
