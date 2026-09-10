from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.task import TaskPriority, TaskStatus
from app.schemas.user import UserResponse
from app.schemas.category import CategoryResponse


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    deadline: datetime
    estimated_hours: Decimal = Field(..., ge=0)
    actual_hours: Optional[Decimal] = Field(None, ge=0)


class TaskCreate(TaskBase):
    user_id: int
    category_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = Field(None, ge=0)
    actual_hours: Optional[Decimal] = Field(None, ge=0)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(TaskBase):
    id: int
    user_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
