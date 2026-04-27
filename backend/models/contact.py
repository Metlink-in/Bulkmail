from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime

class ContactBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    org: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    email_status: Literal["valid", "invalid", "risky", "mx_fail"] = "valid"

class Contact(ContactBase):
    id: str = Field(alias="_id")
    list_id: str
    user_id: str

class ContactListCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ContactList(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

class ContactImportResponse(BaseModel):
    list_id: str
    total_imported: int
    total_failed: int
    errors: List[str]
