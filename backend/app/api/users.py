from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.pagination import PaginatedResponse
from app.services.user_service import UserService
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse[UserResponse], status_code=status.HTTP_200_OK)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """List all platform users (ADMIN privilege required)."""
    service = UserService(db)
    return service.get_users(page=page, limit=limit)


@router.get("/assignable", response_model=PaginatedResponse[UserResponse], status_code=status.HTTP_200_OK)
def get_assignable_users(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignable users list for task creation and assignment (authenticated users)."""
    service = UserService(db)
    return service.get_users(page=page, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user profile by ID (ADMIN or self access)."""
    service = UserService(db)
    return service.get_user_by_id(user_id=user_id, current_user=current_user)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,
    req: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile (ADMIN or self access)."""
    service = UserService(db)
    return service.update_user(user_id=user_id, req=req, current_user=current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Delete user account by ID (ADMIN privilege required)."""
    service = UserService(db)
    service.delete_user(user_id=user_id, current_user=admin_user)
