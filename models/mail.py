from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class MailJobCreate(BaseModel):
    template_id: str
    contact_ids: List[str]
    scheduled_at: Optional[datetime] = None
    interval_seconds: int = 300

class MailJob(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    template_id: str
    contact_ids: List[str]
    status: Literal["draft", "running", "paused", "completed", "failed"]
    scheduled_at: Optional[datetime] = None
    interval_seconds: int = 300
    created_at: datetime
    updated_at: datetime

class MailLogResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    contact_id: str
    sent_at: datetime
    status: Literal["sent", "failed", "bounced", "opened", "clicked"]
    error_message: Optional[str] = None

class MailLog(MailLogResponse):
    id: str = Field(alias="_id")

class MailSendRequest(BaseModel):
    subject: str
    html_body: str
    to_email: str

class MailStatusResponse(BaseModel):
    job_id: str
    status: str
    total_contacts: int
    sent_count: int
    failed_count: int
