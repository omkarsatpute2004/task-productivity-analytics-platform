from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np


def clean_tasks_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean tasks dataframe: deduplicate, validate timestamps, fix invalid negative hours."""
    initial_count = len(df)
    metadata = {
        "initial_count": initial_count,
        "cleaned_count": initial_count,
        "duplicates_removed": 0,
        "missing_completed_at": 0,
        "invalid_hours_fixed": 0
    }

    if df.empty:
        return df, metadata

    # 1. Deduplicate by task_id
    df_clean = df.drop_duplicates(subset=["task_id"]).copy()
    metadata["duplicates_removed"] = initial_count - len(df_clean)

    # 2. Parse Datetime columns safely
    for col in ["created_at", "updated_at", "deadline", "completed_at"]:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], utc=True, errors="coerce")

    # 3. Handle negative hours (if any exist)
    if "estimated_hours" in df_clean.columns:
        invalid_est = (df_clean["estimated_hours"] < 0)
        metadata["invalid_hours_fixed"] += int(invalid_est.sum())
        df_clean.loc[invalid_est, "estimated_hours"] = np.nan

    if "actual_hours" in df_clean.columns:
        invalid_act = (df_clean["actual_hours"] < 0)
        metadata["invalid_hours_fixed"] += int(invalid_act.sum())
        df_clean.loc[invalid_act, "actual_hours"] = np.nan

    # 4. Count missing completed_at for incomplete tasks
    if "completed_at" in df_clean.columns and "status" in df_clean.columns:
        incomplete_mask = df_clean["status"] != "COMPLETED"
        metadata["missing_completed_at"] = int((incomplete_mask & df_clean["completed_at"].isna()).sum())

    metadata["cleaned_count"] = len(df_clean)
    return df_clean, metadata

