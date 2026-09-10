from datetime import datetime
from typing import Optional, Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session

from app.models.user import User
from app.analytics.queries import get_tasks_analytics_dataframe
from app.analytics.cleaning import clean_tasks_dataframe
from app.analytics.features import enrich_task_features
from app.analytics.calculations import (
    compute_summary_kpis,
    compute_status_distribution,
    compute_priority_analysis,
    compute_category_analysis,
    compute_user_productivity,
    compute_department_analysis,
    compute_completion_trend,
    compute_overdue_analysis,
    compute_workload_analysis,
    compute_estimation_analysis
)
from app.analytics.statistics import (
    calculate_descriptive_stats,
    calculate_correlations,
    detect_outliers_iqr
)


class AnalyticsService:

    @staticmethod
    def get_processed_dataframe(
        db: Session,
        current_user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_user_id: Optional[int] = None,
        department: Optional[str] = None,
        category_id: Optional[int] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch, clean, and enrich task dataframe considering RBAC authorization rules."""
        # Non-admin users are restricted to their own data
        effective_user_id = target_user_id
        if current_user.role != "ADMIN":
            effective_user_id = current_user.id

        raw_df = get_tasks_analytics_dataframe(
            db=db,
            start_date=start_date,
            end_date=end_date,
            user_id=effective_user_id,
            department=department,
            category_id=category_id,
            priority=priority,
            status=status
        )

        clean_df, _ = clean_tasks_dataframe(raw_df)
        enriched_df = enrich_task_features(clean_df)
        return enriched_df

    @classmethod
    def get_summary(
        cls,
        db: Session,
        current_user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_user_id: Optional[int] = None,
        department: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            target_user_id=target_user_id,
            department=department,
            category_id=category_id
        )
        return compute_summary_kpis(df)

    @classmethod
    def get_status_distribution(
        cls,
        db: Session,
        current_user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            target_user_id=target_user_id
        )
        return compute_status_distribution(df)

    @classmethod
    def get_priority_analysis(
        cls,
        db: Session,
        current_user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            target_user_id=target_user_id
        )
        return compute_priority_analysis(df)

    @classmethod
    def get_category_analysis(
        cls,
        db: Session,
        current_user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            target_user_id=target_user_id
        )
        return compute_category_analysis(df)

    @classmethod
    def get_user_productivity(
        cls,
        db: Session,
        current_user: User,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            department=department
        )
        return compute_user_productivity(df)

    @classmethod
    def get_department_analysis(
        cls,
        db: Session,
        current_user: User
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user
        )
        return compute_department_analysis(df)

    @classmethod
    def get_completion_trend(
        cls,
        db: Session,
        current_user: User,
        interval: str = "daily",
        target_user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            target_user_id=target_user_id
        )
        return compute_completion_trend(df, interval=interval)

    @classmethod
    def get_overdue_analysis(
        cls,
        db: Session,
        current_user: User,
        target_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            target_user_id=target_user_id
        )
        return compute_overdue_analysis(df)

    @classmethod
    def get_workload_analysis(
        cls,
        db: Session,
        current_user: User,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            department=department
        )
        return compute_workload_analysis(df)

    @classmethod
    def get_estimation_analysis(
        cls,
        db: Session,
        current_user: User,
        target_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        df = cls.get_processed_dataframe(
            db=db,
            current_user=current_user,
            target_user_id=target_user_id
        )
        basic_estimation = compute_estimation_analysis(df)
        
        # Add descriptive statistics, correlations, and outliers
        est_hours_stats = calculate_descriptive_stats(df["estimated_hours"])
        act_hours_stats = calculate_descriptive_stats(df["actual_hours"])
        err_stats = calculate_descriptive_stats(df["estimation_error"])
        correlations = calculate_correlations(df)
        est_outliers = detect_outliers_iqr(df["estimated_hours"])
        act_outliers = detect_outliers_iqr(df["actual_hours"])

        return {
            **basic_estimation,
            "statistics": {
                "estimated_hours": est_hours_stats,
                "actual_hours": act_hours_stats,
                "estimation_error": err_stats,
                "correlations": correlations,
                "outliers": {
                    "estimated_hours": est_outliers,
                    "actual_hours": act_outliers
                }
            }
        }
