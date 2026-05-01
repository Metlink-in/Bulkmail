from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    subject: str
    html_body: str

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    html_body: Optional[str] = None

class TemplateResponse(TemplateBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class TemplateInDB(TemplateResponse):
    id: str = Field(alias="_id")
