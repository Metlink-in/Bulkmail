from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class SmtpConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str  # Will be encrypted before saving

class AiConfig(BaseModel):
    gemini_api_key: str  # Will be encrypted before saving

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    role: str = "user"
    is_active: bool = True
    smtp_config: Optional[SmtpConfig] = None
    ai_config: Optional[AiConfig] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(UserBase):
    id: str
    role: str
    is_active: bool
    has_smtp: bool = False
    has_ai: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool
