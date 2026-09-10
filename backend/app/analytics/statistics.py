from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def calculate_descriptive_stats(series: pd.Series) -> Dict[str, Any]:
    """Calculate summary statistics: mean, median, std, min, max, percentiles (25, 50, 75, 90)."""
    valid_s = series.dropna()
    if valid_s.empty:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p25": 0.0,
            "p50": 0.0,
            "p75": 0.0,
            "p90": 0.0
        }

    return {
        "count": int(len(valid_s)),
        "mean": round(float(valid_s.mean()), 2),
        "median": round(float(valid_s.median()), 2),
        "std": round(float(valid_s.std()), 2) if len(valid_s) > 1 else 0.0,
        "min": round(float(valid_s.min()), 2),
        "max": round(float(valid_s.max()), 2),
        "p25": round(float(valid_s.quantile(0.25)), 2),
        "p50": round(float(valid_s.quantile(0.50)), 2),
        "p75": round(float(valid_s.quantile(0.75)), 2),
        "p90": round(float(valid_s.quantile(0.90)), 2)
    }


def calculate_correlations(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    """Calculate Pearson correlations between numerical metrics."""
    res = {
        "estimated_vs_actual_hours": None,
        "estimated_hours_vs_completion_days": None,
        "actual_hours_vs_completion_days": None
    }

    if df.empty:
        return res

    if "estimated_hours" in df.columns and "actual_hours" in df.columns:
        valid_est_act = df[["estimated_hours", "actual_hours"]].dropna()
        if len(valid_est_act) > 1:
            corr = valid_est_act["estimated_hours"].corr(valid_est_act["actual_hours"])
            if not np.isnan(corr):
                res["estimated_vs_actual_hours"] = round(float(corr), 3)

    if "estimated_hours" in df.columns and "completion_days" in df.columns:
        valid_est_days = df[["estimated_hours", "completion_days"]].dropna()
        if len(valid_est_days) > 1:
            corr = valid_est_days["estimated_hours"].corr(valid_est_days["completion_days"])
            if not np.isnan(corr):
                res["estimated_hours_vs_completion_days"] = round(float(corr), 3)

    if "actual_hours" in df.columns and "completion_days" in df.columns:
        valid_act_days = df[["actual_hours", "completion_days"]].dropna()
        if len(valid_act_days) > 1:
            corr = valid_act_days["actual_hours"].corr(valid_act_days["completion_days"])
            if not np.isnan(corr):
                res["actual_hours_vs_completion_days"] = round(float(corr), 3)

    return res


def detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """Detect outliers using Interquartile Range (IQR) method."""
    valid_s = series.dropna()
    if len(valid_s) < 4:
        return {
            "q1": 0.0,
            "q3": 0.0,
            "iqr": 0.0,
            "lower_bound": 0.0,
            "upper_bound": 0.0,
            "outlier_count": 0,
            "outliers": []
        }

    q1 = float(valid_s.quantile(0.25))
    q3 = float(valid_s.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = valid_s[(valid_s < lower_bound) | (valid_s > upper_bound)].tolist()

    return {
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "outlier_count": len(outliers),
        "outliers": [round(float(v), 2) for v in outliers[:20]]  # Cap list to top 20
    }
