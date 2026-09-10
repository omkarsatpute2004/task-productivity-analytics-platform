from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(func.lower(User.email) == func.lower(email)).first()

    def get_all(self, page: int = 1, limit: int = 20) -> Tuple[List[User], int]:
        total = self.db.query(func.count(User.id)).scalar() or 0
        offset = (page - 1) * limit
        users = self.db.query(User).order_by(User.id.asc()).offset(offset).limit(limit).all()
        return users, total

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
