from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.task_activity import ActivityType


class TaskActivityResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    activity_type: ActivityType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
