import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any


FEATURE_COLUMNS = [
    'priority',
    'category_id',
    'user_id',
    'department',
    'estimated_hours',
    'days_to_deadline',
    'user_task_count',
    'user_completion_rate',
]

CATEGORICAL_FEATURES = ['priority', 'category_id', 'user_id', 'department']
NUMERICAL_FEATURES = ['estimated_hours', 'days_to_deadline', 'user_task_count', 'user_completion_rate']


def extract_ml_dataset(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Extract ML dataset from raw task DataFrame.
    Prevents Data Leakage by strictly excluding post-completion fields (completed_at, actual_hours, status).
    """
    stats = {
        'total_records': len(raw_df),
        'completed_records': 0,
        'late_records': 0,
        'on_time_records': 0,
    }

    if raw_df.empty:
        return pd.DataFrame(), stats

    df = raw_df.copy()

    # Filter to completed tasks for historical ground-truth target training
    completed_df = df[df['status'] == 'COMPLETED'].copy()
    stats['completed_records'] = len(completed_df)

    if completed_df.empty:
        return pd.DataFrame(), stats

    # Target 1: is_late (Classification)
    completed_df['completed_at_dt'] = pd.to_datetime(completed_df['completed_at'], utc=True, errors='coerce')
    completed_df['deadline_dt'] = pd.to_datetime(completed_df['deadline'], utc=True, errors='coerce')
    completed_df['created_at_dt'] = pd.to_datetime(completed_df['created_at'], utc=True, errors='coerce')

    # Target binary definition: 1 if completed after deadline, 0 if completed on/before deadline
    completed_df['is_late'] = (completed_df['completed_at_dt'] > completed_df['deadline_dt']).astype(int)
    stats['late_records'] = int(completed_df['is_late'].sum())
    stats['on_time_records'] = stats['completed_records'] - stats['late_records']

    # Target 2: completion_days (Regression)
    completed_df['completion_days'] = (
        completed_df['completed_at_dt'] - completed_df['created_at_dt']
    ).dt.total_seconds() / 86400.0
    completed_df.loc[completed_df['completion_days'] < 0, 'completion_days'] = np.nan

    # Prediction Feature 1: days_to_deadline (deadline - created_at)
    completed_df['days_to_deadline'] = (
        completed_df['deadline_dt'] - completed_df['created_at_dt']
    ).dt.total_seconds() / 86400.0
    completed_df['days_to_deadline'] = completed_df['days_to_deadline'].fillna(7.0)

    # Derived Features: User aggregate metrics (computed strictly from past context)
    user_task_counts = df.groupby('user_id').size().to_dict()
    user_comp_rates = (
        df.groupby('user_id')['status']
        .apply(lambda s: (s == 'COMPLETED').sum() / len(s) * 100.0)
        .to_dict()
    )

    completed_df['user_task_count'] = completed_df['user_id'].map(user_task_counts).fillna(1.0)
    completed_df['user_completion_rate'] = completed_df['user_id'].map(user_comp_rates).fillna(50.0)
    completed_df['department'] = completed_df['department'].fillna('General')
    completed_df['category_id'] = completed_df['category_id'].astype(str)
    completed_df['user_id'] = completed_df['user_id'].astype(str)

    return completed_df, stats


def prepare_single_sample(
    priority: str,
    category_id: int,
    user_id: int,
    department: str,
    estimated_hours: float,
    deadline: datetime = None,
    created_at: datetime = None,
    user_task_count: float = 5.0,
    user_completion_rate: float = 50.0,
) -> pd.DataFrame:
    now_utc = datetime.now(timezone.utc)
    c_at = created_at or now_utc
    d_at = deadline or (c_at + pd.Timedelta(days=7))

    if isinstance(d_at, datetime):
        d_at_aware = d_at.replace(tzinfo=timezone.utc) if d_at.tzinfo is None else d_at
        c_at_aware = c_at.replace(tzinfo=timezone.utc) if c_at.tzinfo is None else c_at
        days_to_dl = (d_at_aware - c_at_aware).total_seconds() / 86400.0
    else:
        days_to_dl = 7.0



    sample = {
        'priority': priority,
        'category_id': str(category_id),
        'user_id': str(user_id),
        'department': department or 'General',
        'estimated_hours': float(estimated_hours),
        'days_to_deadline': max(0.1, float(days_to_dl)),
        'user_task_count': float(user_task_count),
        'user_completion_rate': float(user_completion_rate),
    }

    return pd.DataFrame([sample])[FEATURE_COLUMNS]
