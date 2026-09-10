from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.analytics.statistics import calculate_descriptive_stats


def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level summary productivity KPIs."""
    total_tasks = len(df)
    if total_tasks == 0:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "cancelled_tasks": 0,
            "overdue_tasks": 0,
            "completion_rate": 0.0,
            "on_time_completion_rate": 0.0,
            "late_completion_rate": 0.0,
            "average_completion_days": 0.0,
            "median_completion_days": 0.0
        }

    completed_tasks = int((df["status"] == "COMPLETED").sum())
    pending_tasks = int((df["status"] == "TODO").sum())
    in_progress_tasks = int((df["status"] == "IN_PROGRESS").sum())
    cancelled_tasks = int((df["status"] == "CANCELLED").sum())
    overdue_tasks = int(df["is_overdue"].sum())

    completion_rate = round((completed_tasks / total_tasks * 100.0), 2) if total_tasks > 0 else 0.0

    on_time_tasks = int(df["is_on_time"].sum())
    late_tasks = int(df["is_late"].sum())

    on_time_completion_rate = round((on_time_tasks / completed_tasks * 100.0), 2) if completed_tasks > 0 else 0.0
    late_completion_rate = round((late_tasks / completed_tasks * 100.0), 2) if completed_tasks > 0 else 0.0

    comp_days_series = df.loc[df["is_completed"], "completion_days"].dropna()
    avg_comp_days = round(float(comp_days_series.mean()), 2) if not comp_days_series.empty else 0.0
    med_comp_days = round(float(comp_days_series.median()), 2) if not comp_days_series.empty else 0.0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "cancelled_tasks": cancelled_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": completion_rate,
        "on_time_completion_rate": on_time_completion_rate,
        "late_completion_rate": late_completion_rate,
        "average_completion_days": avg_comp_days,
        "median_completion_days": med_comp_days
    }


def compute_status_distribution(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute breakdown by task status."""
    total = len(df)
    if total == 0:
        return []

    group = df.groupby("status").size().reset_index(name="count")
    result = []
    for _, row in group.iterrows():
        st = row["status"]
        cnt = int(row["count"])
        pct = round((cnt / total * 100.0), 2)
        result.append({
            "status": st,
            "count": cnt,
            "percentage": pct
        })
    return result


def compute_priority_analysis(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute breakdown by priority (LOW, MEDIUM, HIGH, CRITICAL)."""
    if df.empty:
        return []

    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    result = []
    for prio in priorities:
        sub_df = df[df["priority"] == prio]
        total = len(sub_df)
        if total == 0:
            result.append({
                "priority": prio,
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "overdue_tasks": 0,
                "completion_rate": 0.0,
                "late_completion_rate": 0.0,
                "average_completion_days": 0.0,
                "average_estimated_hours": 0.0,
                "average_actual_hours": 0.0
            })
            continue

        completed = int((sub_df["status"] == "COMPLETED").sum())
        pending = int((sub_df["status"] == "TODO").sum())
        overdue = int(sub_df["is_overdue"].sum())
        late = int(sub_df["is_late"].sum())

        comp_rate = round((completed / total * 100.0), 2)
        late_rate = round((late / completed * 100.0), 2) if completed > 0 else 0.0

        comp_days = sub_df.loc[sub_df["is_completed"], "completion_days"].dropna()
        avg_comp = round(float(comp_days.mean()), 2) if not comp_days.empty else 0.0

        avg_est = round(float(sub_df["estimated_hours"].mean()), 2) if sub_df["estimated_hours"].notna().any() else 0.0
        avg_act = round(float(sub_df["actual_hours"].mean()), 2) if sub_df["actual_hours"].notna().any() else 0.0

        result.append({
            "priority": prio,
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "overdue_tasks": overdue,
            "completion_rate": comp_rate,
            "late_completion_rate": late_rate,
            "average_completion_days": avg_comp,
            "average_estimated_hours": avg_est,
            "average_actual_hours": avg_act
        })
    return result


def compute_category_analysis(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute breakdown by Category."""
    if df.empty:
        return []

    result = []
    groups = df.groupby(["category_id", "category_name"])
    for (cat_id, cat_name), sub_df in groups:
        total = len(sub_df)
        completed = int((sub_df["status"] == "COMPLETED").sum())
        overdue = int(sub_df["is_overdue"].sum())
        late = int(sub_df["is_late"].sum())

        comp_rate = round((completed / total * 100.0), 2) if total > 0 else 0.0
        late_rate = round((late / completed * 100.0), 2) if completed > 0 else 0.0

        comp_days = sub_df.loc[sub_df["is_completed"], "completion_days"].dropna()
        avg_comp = round(float(comp_days.mean()), 2) if not comp_days.empty else 0.0

        total_est = round(float(sub_df["estimated_hours"].sum()), 2) if sub_df["estimated_hours"].notna().any() else 0.0
        total_act = round(float(sub_df["actual_hours"].sum()), 2) if sub_df["actual_hours"].notna().any() else 0.0

        result.append({
            "category_id": int(cat_id),
            "category_name": str(cat_name),
            "total_tasks": total,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "late_tasks": late,
            "completion_rate": comp_rate,
            "late_completion_rate": late_rate,
            "average_completion_days": avg_comp,
            "total_estimated_hours": total_est,
            "total_actual_hours": total_act
        })
    return sorted(result, key=lambda x: x["total_tasks"], reverse=True)


def compute_user_productivity(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute neutral user productivity metrics."""
    if df.empty:
        return []

    result = []
    groups = df.groupby(["user_id", "user_name", "department"])
    for (uid, uname, dept), sub_df in groups:
        total = len(sub_df)
        completed = int((sub_df["status"] == "COMPLETED").sum())
        pending = int((sub_df["status"] == "TODO").sum())
        in_prog = int((sub_df["status"] == "IN_PROGRESS").sum())
        overdue = int(sub_df["is_overdue"].sum())

        comp_rate = round((completed / total * 100.0), 2) if total > 0 else 0.0
        on_time = int(sub_df["is_on_time"].sum())
        late = int(sub_df["is_late"].sum())

        on_time_rate = round((on_time / completed * 100.0), 2) if completed > 0 else 0.0
        late_rate = round((late / completed * 100.0), 2) if completed > 0 else 0.0

        comp_days = sub_df.loc[sub_df["is_completed"], "completion_days"].dropna()
        avg_comp = round(float(comp_days.mean()), 2) if not comp_days.empty else 0.0

        tot_est = round(float(sub_df["estimated_hours"].sum()), 2) if sub_df["estimated_hours"].notna().any() else 0.0
        tot_act = round(float(sub_df["actual_hours"].sum()), 2) if sub_df["actual_hours"].notna().any() else 0.0

        result.append({
            "user_id": int(uid),
            "user_name": str(uname),
            "department": str(dept) if pd.notna(dept) else None,
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_prog,
            "overdue_tasks": overdue,
            "completion_rate": comp_rate,
            "on_time_completion_rate": on_time_rate,
            "late_completion_rate": late_rate,
            "average_completion_days": avg_comp,
            "total_estimated_hours": tot_est,
            "total_actual_hours": tot_act
        })
    return sorted(result, key=lambda x: x["completion_rate"], reverse=True)


def compute_department_analysis(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute breakdown by Department."""
    if df.empty or "department" not in df.columns:
        return []

    result = []
    groups = df.groupby("department")
    for dept, sub_df in groups:
        if pd.isna(dept) or not dept:
            continue
        total = len(sub_df)
        completed = int((sub_df["status"] == "COMPLETED").sum())
        overdue = int(sub_df["is_overdue"].sum())

        comp_rate = round((completed / total * 100.0), 2) if total > 0 else 0.0

        comp_days = sub_df.loc[sub_df["is_completed"], "completion_days"].dropna()
        avg_comp = round(float(comp_days.mean()), 2) if not comp_days.empty else 0.0

        tot_est = round(float(sub_df["estimated_hours"].sum()), 2) if sub_df["estimated_hours"].notna().any() else 0.0
        tot_act = round(float(sub_df["actual_hours"].sum()), 2) if sub_df["actual_hours"].notna().any() else 0.0

        result.append({
            "department": str(dept),
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": comp_rate,
            "overdue_tasks": overdue,
            "average_completion_days": avg_comp,
            "total_estimated_hours": tot_est,
            "total_actual_hours": tot_act
        })
    return sorted(result, key=lambda x: x["total_tasks"], reverse=True)


def compute_completion_trend(df: pd.DataFrame, interval: str = "daily") -> List[Dict[str, Any]]:
    """Compute time series completion trends (daily, weekly, monthly)."""
    if df.empty or "created_at" not in df.columns:
        return []

    df_time = df.copy()
    df_time["created_at"] = pd.to_datetime(df_time["created_at"], utc=True)

    if interval == "monthly":
        df_time["period"] = df_time["created_at"].dt.to_period("M").astype(str)
    elif interval == "weekly":
        df_time["period"] = df_time["created_at"].dt.to_period("W").astype(str)
    else:
        df_time["period"] = df_time["created_at"].dt.strftime("%Y-%m-%d")

    groups = df_time.groupby("period")
    result = []
    for period, sub_df in groups:
        created = len(sub_df)
        completed = int((sub_df["status"] == "COMPLETED").sum())
        overdue = int(sub_df["is_overdue"].sum())
        comp_rate = round((completed / created * 100.0), 2) if created > 0 else 0.0

        result.append({
            "period": str(period),
            "tasks_created": created,
            "tasks_completed": completed,
            "tasks_overdue": overdue,
            "completion_rate": comp_rate
        })
    return sorted(result, key=lambda x: x["period"])


def compute_overdue_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute detailed overdue task analytics."""
    if df.empty:
        return {
            "total_overdue": 0,
            "incomplete_overdue": 0,
            "completed_late": 0,
            "overdue_by_priority": [],
            "overdue_by_category": []
        }

    overdue_df = df[df["is_overdue"]]
    total_overdue = len(overdue_df)
    incomplete_overdue = int((~df["status"].isin(["COMPLETED", "CANCELLED"]) & df["is_overdue"]).sum())
    completed_late = int(df["is_late"].sum())

    prio_group = overdue_df.groupby("priority").size().to_dict() if not overdue_df.empty else {}
    cat_group = overdue_df.groupby("category_name").size().to_dict() if not overdue_df.empty else {}

    return {
        "total_overdue": total_overdue,
        "incomplete_overdue": incomplete_overdue,
        "completed_late": completed_late,
        "overdue_by_priority": [{"priority": k, "count": int(v)} for k, v in prio_group.items()],
        "overdue_by_category": [{"category_name": k, "count": int(v)} for k, v in cat_group.items()]
    }


def compute_workload_analysis(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compute open workload distribution per user."""
    if df.empty:
        return []

    result = []
    groups = df.groupby(["user_id", "user_name"])
    for (uid, uname), sub_df in groups:
        tot_assigned = len(sub_df)
        open_tasks = sub_df[~sub_df["status"].isin(["COMPLETED", "CANCELLED"])]
        open_count = len(open_tasks)
        high_open = int((open_tasks["priority"] == "HIGH").sum())
        crit_open = int((open_tasks["priority"] == "CRITICAL").sum())
        overdue_open = int(open_tasks["is_overdue"].sum())

        comp_tasks = (sub_df["status"] == "COMPLETED").sum()
        comp_rate = round((comp_tasks / tot_assigned * 100.0), 2) if tot_assigned > 0 else 0.0

        result.append({
            "user_id": int(uid),
            "user_name": str(uname),
            "total_assigned_tasks": tot_assigned,
            "open_tasks": open_count,
            "high_priority_open_tasks": high_open,
            "critical_priority_open_tasks": crit_open,
            "overdue_open_tasks": overdue_open,
            "completion_rate": comp_rate
        })
    return sorted(result, key=lambda x: x["open_tasks"], reverse=True)


def compute_estimation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute Estimated vs Actual Hours estimation error analysis."""
    if df.empty or "estimated_hours" not in df.columns:
        return {
            "total_estimated_hours": 0.0,
            "total_actual_hours": 0.0,
            "average_estimated_hours": 0.0,
            "average_actual_hours": 0.0,
            "total_estimation_error": 0.0,
            "average_estimation_error": 0.0,
            "average_estimation_error_percentage": 0.0,
            "underestimated_tasks_count": 0,
            "overestimated_tasks_count": 0
        }

    valid_est = df["estimated_hours"].dropna()
    valid_act = df["actual_hours"].dropna()

    tot_est = round(float(valid_est.sum()), 2) if not valid_est.empty else 0.0
    tot_act = round(float(valid_act.sum()), 2) if not valid_act.empty else 0.0
    avg_est = round(float(valid_est.mean()), 2) if not valid_est.empty else 0.0
    avg_act = round(float(valid_act.mean()), 2) if not valid_act.empty else 0.0

    err_series = df["estimation_error"].dropna()
    tot_err = round(float(err_series.sum()), 2) if not err_series.empty else 0.0
    avg_err = round(float(err_series.mean()), 2) if not err_series.empty else 0.0

    pct_series = df["estimation_error_percentage"].dropna()
    avg_pct = round(float(pct_series.mean()), 2) if not pct_series.empty else 0.0

    underestimated = int((err_series > 0).sum())
    overestimated = int((err_series < 0).sum())

    return {
        "total_estimated_hours": tot_est,
        "total_actual_hours": tot_act,
        "average_estimated_hours": avg_est,
        "average_actual_hours": avg_act,
        "total_estimation_error": tot_err,
        "average_estimation_error": avg_err,
        "average_estimation_error_percentage": avg_pct,
        "underestimated_tasks_count": underestimated,
        "overestimated_tasks_count": overestimated
    }
