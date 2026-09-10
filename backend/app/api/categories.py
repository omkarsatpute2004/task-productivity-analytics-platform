from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from app.api.deps import get_current_user, require_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all categories."""
    service = CategoryService(db)
    return service.get_all_categories()


@router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get category details by ID."""
    service = CategoryService(db)
    return service.get_category_by_id(category_id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    req: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Create a new category (ADMIN privilege required)."""
    service = CategoryService(db)
    return service.create_category(req)


@router.put("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category(
    category_id: int,
    req: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Update a category (ADMIN privilege required)."""
    service = CategoryService(db)
    return service.update_category(category_id=category_id, req=req)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Delete a category by ID (ADMIN privilege required)."""
    service = CategoryService(db)
    service.delete_category(category_id)
