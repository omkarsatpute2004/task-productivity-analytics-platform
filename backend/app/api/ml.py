from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.api.deps import get_current_user
from app.ml.model_manager import ModelManager
from app.ml.schemas import (
    OverduePredictionRequest,
    OverduePredictionResponse,
    CompletionTimePredictionRequest,
    CompletionTimePredictionResponse,
    ModelInfoResponse,
    FeatureImportanceResponse
)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/predict-overdue", response_model=OverduePredictionResponse, status_code=status.HTTP_200_OK)
def predict_overdue(
    req: OverduePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Predict task overdue probability and risk level (LOW, MEDIUM, HIGH) using trained ML model."""
    # Data Privacy & Authorization: Non-admin users cannot request predictions for other users
    if current_user.role != UserRole.ADMIN and req.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request prediction for another user."
        )

    manager = ModelManager.get_instance()
    res = manager.predict_overdue(
        priority=req.priority,
        category_id=req.category_id,
        user_id=req.user_id,
        estimated_hours=req.estimated_hours,
        department=current_user.department,
        deadline=req.deadline
    )
    return OverduePredictionResponse(**res)


@router.post("/predict-completion-time", response_model=CompletionTimePredictionResponse, status_code=status.HTTP_200_OK)
def predict_completion_time(
    req: CompletionTimePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Predict task completion duration in days using trained regression model."""
    if current_user.role != UserRole.ADMIN and req.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to request prediction for another user."
        )

    manager = ModelManager.get_instance()
    res = manager.predict_completion_time(
        priority=req.priority,
        category_id=req.category_id,
        user_id=req.user_id,
        estimated_hours=req.estimated_hours,
        department=current_user.department
    )
    return CompletionTimePredictionResponse(**res)


@router.get("/model-info", status_code=status.HTTP_200_OK)
def get_model_info(
    current_user: User = Depends(get_current_user)
):
    """Get metadata, dataset size, training timestamp, and evaluation metrics for active ML models."""
    manager = ModelManager.get_instance()
    return manager.get_model_info()


@router.get("/feature-importance", response_model=FeatureImportanceResponse, status_code=status.HTTP_200_OK)
def get_feature_importance(
    current_user: User = Depends(get_current_user)
):
    """Get interpretable feature importance factors used by the ML classification and regression models."""
    manager = ModelManager.get_instance()
    return FeatureImportanceResponse(**manager.get_feature_importance())


@router.get("/health", status_code=status.HTTP_200_OK)
def ml_health_check(
    current_user: User = Depends(get_current_user)
):
    """Check machine learning model load status."""
    manager = ModelManager.get_instance()
    ready = manager.is_ready()
    return {
        "status": "ok" if ready else "degraded",
        "models_loaded": ready,
        "classification_active": manager.clf_pipeline is not None,
        "regression_active": manager.reg_pipeline is not None
    }
