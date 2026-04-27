from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CampaignBase(BaseModel):
    name: str
    subject_template: str
    body_template: str
    use_ai_personalization: bool = False

class CampaignCreate(CampaignBase):
    pass

class CampaignInDB(CampaignBase):
    id: str = Field(alias="_id")
    user_id: str
    status: str = "draft"  # draft, running, paused, completed
    sent_count: int = 0
    total_recipients: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CampaignResponse(CampaignBase):
    id: str
    status: str
    sent_count: int
    total_recipients: int
    created_at: datetime
    updated_at: datetime
