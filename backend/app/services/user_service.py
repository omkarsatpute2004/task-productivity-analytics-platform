import math
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.pagination import PaginatedResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_users(self, page: int = 1, limit: int = 20) -> PaginatedResponse[UserResponse]:
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        users, total = self.user_repo.get_all(page=page, limit=limit)
        pages = math.ceil(total / limit) if total > 0 else 0
        items = [UserResponse.model_validate(u) for u in users]
        return PaginatedResponse(
            items=items,
            page=page,
            limit=limit,
            total=total,
            pages=pages
        )

    def get_user_by_id(self, user_id: int, current_user: User) -> UserResponse:
        # Authorization check: ADMIN or self
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this user profile."
            )

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )
        return UserResponse.model_validate(user)

    def update_user(self, user_id: int, req: UserUpdate, current_user: User) -> UserResponse:
        # Authorization check: ADMIN or self
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this user profile."
            )

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )

        # Non-admin users cannot change their own role
        if req.role is not None and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can modify user roles."
            )

        if req.name is not None:
            user.name = req.name
        if req.department is not None:
            user.department = req.department
        if req.role is not None and current_user.role == UserRole.ADMIN:
            user.role = req.role

        updated_user = self.user_repo.update(user)
        return UserResponse.model_validate(updated_user)

    def delete_user(self, user_id: int, current_user: User) -> None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete user accounts."
            )

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found."
            )

        self.user_repo.delete(user)
