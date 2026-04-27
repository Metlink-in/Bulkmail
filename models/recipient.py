from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
from datetime import datetime

class RecipientBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RecipientCreate(RecipientBase):
    campaign_id: str

class RecipientInDB(RecipientBase):
    id: str = Field(alias="_id")
    campaign_id: str
    user_id: str
    status: str = "pending"  # pending, sent, failed
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

class RecipientResponse(RecipientBase):
    id: str
    campaign_id: str
    status: str
    sent_at: Optional[datetime]
    error_message: Optional[str]
