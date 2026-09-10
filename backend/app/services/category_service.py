from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.cat_repo = CategoryRepository(db)

    def get_all_categories(self) -> List[CategoryResponse]:
        categories = self.cat_repo.get_all()
        return [CategoryResponse.model_validate(c) for c in categories]

    def get_category_by_id(self, category_id: int) -> CategoryResponse:
        cat = self.cat_repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found."
            )
        return CategoryResponse.model_validate(cat)

    def create_category(self, req: CategoryCreate) -> CategoryResponse:
        existing = self.cat_repo.get_by_name(req.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{req.name}' already exists."
            )

        cat = Category(
            name=req.name,
            description=req.description
        )
        created_cat = self.cat_repo.create(cat)
        return CategoryResponse.model_validate(created_cat)

    def update_category(self, category_id: int, req: CategoryUpdate) -> CategoryResponse:
        cat = self.cat_repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found."
            )

        if req.name is not None and req.name.lower() != cat.name.lower():
            existing = self.cat_repo.get_by_name(req.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category '{req.name}' already exists."
                )
            cat.name = req.name

        if req.description is not None:
            cat.description = req.description

        updated_cat = self.cat_repo.update(cat)
        return CategoryResponse.model_validate(updated_cat)

    def delete_category(self, category_id: int) -> None:
        cat = self.cat_repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found."
            )

        # Check if any tasks reference this category
        task_count = self.cat_repo.count_tasks(category_id)
        if task_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category '{cat.name}' because {task_count} task(s) reference it."
            )

        self.cat_repo.delete(cat)
