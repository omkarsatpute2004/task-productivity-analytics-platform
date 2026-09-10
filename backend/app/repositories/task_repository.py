from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.models.task import Task, TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).options(
            joinedload(Task.user),
            joinedload(Task.category)
        ).filter(Task.id == task_id).first()

    def get_filtered(
        self,
        search: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Task], int]:
        query = self.db.query(Task).options(
            joinedload(Task.user),
            joinedload(Task.category)
        )

        # Filters
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )

        if status:
            query = query.filter(Task.status == status)

        if priority:
            query = query.filter(Task.priority == priority)

        if category_id:
            query = query.filter(Task.category_id == category_id)

        if user_id:
            query = query.filter(Task.user_id == user_id)

        if start_date:
            query = query.filter(Task.created_at >= start_date)

        if end_date:
            query = query.filter(Task.created_at <= end_date)

        # Count total matches before pagination
        total = query.with_entities(func.count(Task.id)).scalar() or 0

        # Sorting
        sort_attr = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_attr.desc())
        else:
            query = query.order_by(sort_attr.asc())

        # Pagination
        offset = (page - 1) * limit
        tasks = query.offset(offset).limit(limit).all()

        return tasks, total

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return self.get_by_id(task.id) or task

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return self.get_by_id(task.id) or task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
