from datetime import datetime, timezone
import pandas as pd
import numpy as np


def enrich_task_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer derived analytics features on tasks dataframe."""
    if df.empty:
        df["completion_days"] = np.nan
        df["days_to_deadline"] = np.nan
        df["is_completed"] = False
        df["is_overdue"] = False
        df["is_late"] = False
        df["is_on_time"] = False
        df["estimation_error"] = np.nan
        df["estimation_error_percentage"] = np.nan
        return df

    df = df.copy()
    now_utc = pd.Timestamp(datetime.now(timezone.utc))

    # 1. completion_days: (completed_at - created_at) in days for COMPLETED tasks
    completed_mask = (df["status"] == "COMPLETED") & df["completed_at"].notna() & df["created_at"].notna()
    df["completion_days"] = np.nan
    df.loc[completed_mask, "completion_days"] = (
        df.loc[completed_mask, "completed_at"] - df.loc[completed_mask, "created_at"]
    ).dt.total_seconds() / 86400.0

    # Ensure no negative completion days
    df.loc[df["completion_days"] < 0, "completion_days"] = np.nan

    # 2. days_to_deadline: (deadline - created_at) in days
    valid_deadline_mask = df["deadline"].notna() & df["created_at"].notna()
    df["days_to_deadline"] = np.nan
    df.loc[valid_deadline_mask, "days_to_deadline"] = (
        df.loc[valid_deadline_mask, "deadline"] - df.loc[valid_deadline_mask, "created_at"]
    ).dt.total_seconds() / 86400.0

    # 3. Boolean flags
    df["is_completed"] = df["status"] == "COMPLETED"

    # Overdue Definition:
    # - Incomplete task: status not in (COMPLETED, CANCELLED) and now > deadline
    # - Completed task: completed_at > deadline
    incomplete_overdue = (~df["status"].isin(["COMPLETED", "CANCELLED"])) & (df["deadline"] < now_utc)
    completed_overdue = (df["status"] == "COMPLETED") & (df["completed_at"] > df["deadline"])
    df["is_overdue"] = incomplete_overdue | completed_overdue

    # Late Completion: completed task where completed_at > deadline
    df["is_late"] = (df["status"] == "COMPLETED") & (df["completed_at"] > df["deadline"])

    # On-Time Completion: completed task where completed_at <= deadline
    df["is_on_time"] = (df["status"] == "COMPLETED") & (df["completed_at"] <= df["deadline"])

    # 4. Estimation Error Metrics: actual_hours - estimated_hours
    df["estimated_hours"] = pd.to_numeric(df["estimated_hours"], errors="coerce")
    df["actual_hours"] = pd.to_numeric(df["actual_hours"], errors="coerce")

    valid_hours_mask = df["actual_hours"].notna() & df["estimated_hours"].notna()
    df["estimation_error"] = np.nan
    if valid_hours_mask.any():
        df.loc[valid_hours_mask, "estimation_error"] = (
            df.loc[valid_hours_mask, "actual_hours"] - df.loc[valid_hours_mask, "estimated_hours"]
        )

    df["estimation_error_percentage"] = np.nan
    valid_est_pct = valid_hours_mask & (df["estimated_hours"] > 0)
    if valid_est_pct.any():
        df.loc[valid_est_pct, "estimation_error_percentage"] = (
            (df.loc[valid_est_pct, "actual_hours"] - df.loc[valid_est_pct, "estimated_hours"])
            / df.loc[valid_est_pct, "estimated_hours"] * 100.0
        )


    return df
