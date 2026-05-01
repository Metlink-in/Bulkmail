from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ScheduledTaskBase(BaseModel):
    job_id: str
    cron_expression: Optional[str] = None
    frequency: Optional[str] = None
    recurrence_type: Optional[str] = None
    next_run: Optional[datetime] = None
    is_active: bool = True
    template_id: str
    contact_ids: List[str]

class ScheduledTaskCreate(ScheduledTaskBase):
    pass

class ScheduledTaskUpdate(BaseModel):
    cron_expression: Optional[str] = None
    frequency: Optional[str] = None
    recurrence_type: Optional[str] = None
    next_run: Optional[datetime] = None
    is_active: Optional[bool] = None
    template_id: Optional[str] = None
    contact_ids: Optional[List[str]] = None

class ScheduledTask(ScheduledTaskBase):
    id: str = Field(alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
