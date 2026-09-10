from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from app.schemas.task_activity import TaskActivityResponse
from app.schemas.pagination import PaginatedResponse
from app.services.task_service import TaskService
from app.api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    req: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task."""
    service = TaskService(db)
    return service.create_task(req=req, current_user=current_user)


@router.get("", response_model=PaginatedResponse[TaskResponse], status_code=status.HTTP_200_OK)
def list_tasks(
    search: Optional[str] = Query(None, description="Search term for title or description"),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID (ADMIN only)"),
    start_date: Optional[datetime] = Query(None, description="Filter by creation start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by creation end date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List, search, filter, and paginate tasks."""
    service = TaskService(db)
    return service.get_tasks(
        search=search,
        status_filter=status,
        priority_filter=priority,
        category_id=category_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user
    )


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task details by ID."""
    service = TaskService(db)
    return service.get_task_by_id(task_id=task_id, current_user=current_user)


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    req: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task details."""
    service = TaskService(db)
    return service.update_task(task_id=task_id, req=req, current_user=current_user)


@router.patch("/{task_id}/status", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task_status(
    task_id: int,
    req: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update task status and record activity log."""
    service = TaskService(db)
    return service.update_task_status(task_id=task_id, req=req, current_user=current_user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task by ID."""
    service = TaskService(db)
    service.delete_task(task_id=task_id, current_user=current_user)


@router.get("/{task_id}/activity", response_model=List[TaskActivityResponse], status_code=status.HTTP_200_OK)
def get_task_activities(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task activity logs."""
    service = TaskService(db)
    return service.get_task_activities(task_id=task_id, current_user=current_user)
