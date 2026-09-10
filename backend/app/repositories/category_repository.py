from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.category import Category
from app.models.task import Task


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(func.lower(Category.name) == func.lower(name)).first()

    def get_all(self) -> List[Category]:
        return self.db.query(Category).order_by(Category.name.asc()).all()

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()

    def count_tasks(self, category_id: int) -> int:
        return self.db.query(func.count(Task.id)).filter(Task.category_id == category_id).scalar() or 0
