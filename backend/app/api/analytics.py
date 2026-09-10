from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", status_code=status.HTTP_200_OK)
def get_analytics_summary(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    user_id: Optional[int] = Query(None, description="Filter by user ID (ADMIN only or self)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get high-level summary KPIs (total tasks, completion rate, overdue count, average completion days)."""
    return AnalyticsService.get_summary(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        target_user_id=user_id,
        department=department,
        category_id=category_id
    )


@router.get("/status-distribution", status_code=status.HTTP_200_OK)
def get_status_distribution(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get task status distribution counts and percentages."""
    return AnalyticsService.get_status_distribution(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        target_user_id=user_id
    )


@router.get("/priority", status_code=status.HTTP_200_OK)
def get_priority_analysis(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get analytics breakdown by priority (LOW, MEDIUM, HIGH, CRITICAL)."""
    return AnalyticsService.get_priority_analysis(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        target_user_id=user_id
    )


@router.get("/categories", status_code=status.HTTP_200_OK)
def get_category_analysis(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get analytics breakdown by task category."""
    return AnalyticsService.get_category_analysis(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        target_user_id=user_id
    )


@router.get("/users", status_code=status.HTTP_200_OK)
def get_user_productivity(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get user productivity metrics using neutral performance measures."""
    return AnalyticsService.get_user_productivity(
        db=db,
        current_user=current_user,
        department=department
    )


@router.get("/departments", status_code=status.HTTP_200_OK)
def get_department_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get productivity analytics grouped by user department."""
    return AnalyticsService.get_department_analysis(
        db=db,
        current_user=current_user
    )


@router.get("/completion-trend", status_code=status.HTTP_200_OK)
def get_completion_trend(
    interval: str = Query("daily", pattern="^(daily|weekly|monthly)$", description="Aggregation interval"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get time-series analysis of task creation and completion rates."""
    return AnalyticsService.get_completion_trend(
        db=db,
        current_user=current_user,
        interval=interval,
        target_user_id=user_id
    )


@router.get("/overdue", status_code=status.HTTP_200_OK)
def get_overdue_analysis(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get overdue task details, broken down by priority and category."""
    return AnalyticsService.get_overdue_analysis(
        db=db,
        current_user=current_user,
        target_user_id=user_id
    )


@router.get("/workload", status_code=status.HTTP_200_OK)
def get_workload_analysis(
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get workload distribution and open high/critical priority task counts per user."""
    return AnalyticsService.get_workload_analysis(
        db=db,
        current_user=current_user,
        department=department
    )


@router.get("/estimation", status_code=status.HTTP_200_OK)
def get_estimation_analysis(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get estimated vs actual hours analysis, estimation error, descriptive statistics, correlations, and outliers."""
    return AnalyticsService.get_estimation_analysis(
        db=db,
        current_user=current_user,
        target_user_id=user_id
    )
