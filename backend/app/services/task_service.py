import math
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.task_activity import TaskActivity, ActivityType
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.activity_repository import ActivityRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from app.schemas.task_activity import TaskActivityResponse
from app.schemas.pagination import PaginatedResponse


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)
        self.cat_repo = CategoryRepository(db)
        self.act_repo = ActivityRepository(db)

    def create_task(self, req: TaskCreate, current_user: User) -> TaskResponse:
        # User role restriction: USER can only assign tasks to themselves
        if current_user.role != UserRole.ADMIN and req.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Standard users can only create and assign tasks to themselves."
            )

        # Validate referenced user
        assignee = self.user_repo.get_by_id(req.user_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned user with ID {req.user_id} not found."
            )

        # Validate referenced category
        category = self.cat_repo.get_by_id(req.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {req.category_id} not found."
            )

        now = datetime.now(timezone.utc)
        completed_at = now if req.status == TaskStatus.COMPLETED else None

        task = Task(
            title=req.title,
            description=req.description,
            user_id=req.user_id,
            category_id=req.category_id,
            priority=req.priority,
            status=req.status,
            created_at=now,
            updated_at=now,
            deadline=req.deadline,
            completed_at=completed_at,
            estimated_hours=req.estimated_hours,
            actual_hours=req.actual_hours
        )
        created_task = self.task_repo.create(task)

        # Log TASK_CREATED activity
        activity = TaskActivity(
            task_id=created_task.id,
            user_id=current_user.id,
            activity_type=ActivityType.TASK_CREATED,
            old_value=None,
            new_value=f"Task '{created_task.title}' created with status {created_task.status.value}",
            created_at=now
        )
        self.act_repo.create(activity)

        return TaskResponse.model_validate(created_task)

    def get_tasks(
        self,
        search: Optional[str] = None,
        status_filter: Optional[TaskStatus] = None,
        priority_filter: Optional[TaskPriority] = None,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        current_user: User = None
    ) -> PaginatedResponse[TaskResponse]:
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        # Backend Authorization: Standard users can only view their assigned tasks
        effective_user_id = user_id
        if current_user.role != UserRole.ADMIN:
            effective_user_id = current_user.id

        tasks, total = self.task_repo.get_filtered(
            search=search,
            status=status_filter,
            priority=priority_filter,
            category_id=category_id,
            user_id=effective_user_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )

        pages = math.ceil(total / limit) if total > 0 else 0
        items = [TaskResponse.model_validate(t) for t in tasks]
        return PaginatedResponse(
            items=items,
            page=page,
            limit=limit,
            total=total,
            pages=pages
        )

    def get_task_by_id(self, task_id: int, current_user: User) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )

        # Access Control: ADMIN or assigned user
        if current_user.role != UserRole.ADMIN and task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this task."
            )

        return TaskResponse.model_validate(task)

    def update_task(self, task_id: int, req: TaskUpdate, current_user: User) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )

        if current_user.role != UserRole.ADMIN and task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to modify this task."
            )

        old_title = task.title
        now = datetime.now(timezone.utc)

        if req.title is not None:
            task.title = req.title
        if req.description is not None:
            task.description = req.description
        if req.category_id is not None:
            category = self.cat_repo.get_by_id(req.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID {req.category_id} not found."
                )
            task.category_id = req.category_id
        if req.user_id is not None and current_user.role == UserRole.ADMIN:
            assignee = self.user_repo.get_by_id(req.user_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {req.user_id} not found."
                )
            task.user_id = req.user_id
        if req.priority is not None:
            task.priority = req.priority
        if req.deadline is not None:
            task.deadline = req.deadline
        if req.estimated_hours is not None:
            task.estimated_hours = req.estimated_hours
        if req.actual_hours is not None:
            task.actual_hours = req.actual_hours

        task.updated_at = now
        updated_task = self.task_repo.update(task)

        # Log TASK_UPDATED activity
        activity = TaskActivity(
            task_id=updated_task.id,
            user_id=current_user.id,
            activity_type=ActivityType.TASK_UPDATED,
            old_value=f"Title: {old_title}",
            new_value=f"Title: {updated_task.title}",
            created_at=now
        )
        self.act_repo.create(activity)

        return TaskResponse.model_validate(updated_task)

    def update_task_status(self, task_id: int, req: TaskStatusUpdate, current_user: User) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )

        if current_user.role != UserRole.ADMIN and task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this task's status."
            )

        old_status = task.status.value
        new_status = req.status.value
        now = datetime.now(timezone.utc)

        task.status = req.status
        task.updated_at = now

        # Handling completed_at timestamp consistently:
        # 1. When status changes to COMPLETED: set completed_at to current UTC timestamp.
        # 2. When a COMPLETED task is reopened (e.g. COMPLETED -> TODO or IN_PROGRESS): reset completed_at to None.
        if req.status == TaskStatus.COMPLETED:
            task.completed_at = now
        elif old_status == TaskStatus.COMPLETED.value and req.status != TaskStatus.COMPLETED:
            task.completed_at = None

        updated_task = self.task_repo.update(task)

        # Log STATUS_CHANGED activity
        act_status = TaskActivity(
            task_id=updated_task.id,
            user_id=current_user.id,
            activity_type=ActivityType.STATUS_CHANGED,
            old_value=old_status,
            new_value=new_status,
            created_at=now
        )
        self.act_repo.create(act_status)

        # Log TASK_COMPLETED activity if completed
        if req.status == TaskStatus.COMPLETED:
            act_comp = TaskActivity(
                task_id=updated_task.id,
                user_id=current_user.id,
                activity_type=ActivityType.TASK_COMPLETED,
                old_value=None,
                new_value=f"Task marked as COMPLETED at {now.isoformat()}",
                created_at=now
            )
            self.act_repo.create(act_comp)

        return TaskResponse.model_validate(updated_task)

    def delete_task(self, task_id: int, current_user: User) -> None:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )

        if current_user.role != UserRole.ADMIN and task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this task."
            )

        now = datetime.now(timezone.utc)

        # Log TASK_DELETED activity before deletion
        activity = TaskActivity(
            task_id=task.id,
            user_id=current_user.id,
            activity_type=ActivityType.TASK_DELETED,
            old_value=f"Title: {task.title}",
            new_value="Task deleted",
            created_at=now
        )
        self.act_repo.create(activity)

        self.task_repo.delete(task)

    def get_task_activities(self, task_id: int, current_user: User) -> List[TaskActivityResponse]:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )

        if current_user.role != UserRole.ADMIN and task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view activity logs for this task."
            )

        activities = self.act_repo.get_by_task_id(task_id)
        return [TaskActivityResponse.model_validate(a) for a in activities]
