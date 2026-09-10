from typing import List
from sqlalchemy.orm import Session
from app.models.task_activity import TaskActivity


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, activity: TaskActivity) -> TaskActivity:
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_by_task_id(self, task_id: int) -> List[TaskActivity]:
        return self.db.query(TaskActivity).filter(
            TaskActivity.task_id == task_id
        ).order_by(TaskActivity.created_at.asc()).all()
