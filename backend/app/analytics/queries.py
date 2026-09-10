from datetime import datetime
from typing import Optional
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text


def get_tasks_analytics_dataframe(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[int] = None,
    department: Optional[str] = None,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None
) -> pd.DataFrame:
    """Execute SQL query joining tasks, users, and categories to extract analytics dataset."""
    query = """
        SELECT 
            t.id AS task_id,
            t.title,
            t.description,
            t.user_id,
            u.name AS user_name,
            u.department,
            u.role AS user_role,
            t.category_id,
            c.name AS category_name,
            t.priority,
            t.status,
            t.created_at,
            t.updated_at,
            t.deadline,
            t.completed_at,
            CAST(t.estimated_hours AS FLOAT) AS estimated_hours,
            CAST(t.actual_hours AS FLOAT) AS actual_hours
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = {}

    if start_date:
        query += " AND t.created_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND t.created_at <= :end_date"
        params["end_date"] = end_date
    if user_id:
        query += " AND t.user_id = :user_id"
        params["user_id"] = user_id
    if department:
        query += " AND u.department = :department"
        params["department"] = department
    if category_id:
        query += " AND t.category_id = :category_id"
        params["category_id"] = category_id
    if priority:
        query += " AND t.priority = :priority"
        params["priority"] = priority
    if status:
        query += " AND t.status = :status"
        params["status"] = status

    result = db.execute(text(query), params)
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows, columns=columns)
    return df


def get_activities_analytics_dataframe(
    db: Session,
    task_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> pd.DataFrame:
    """Execute SQL query extracting task_activity audit records."""
    query = """
        SELECT 
            a.id AS activity_id,
            a.task_id,
            a.user_id,
            u.name AS user_name,
            a.activity_type,
            a.old_value,
            a.new_value,
            a.created_at
        FROM task_activity a
        JOIN users u ON a.user_id = u.id
        WHERE 1=1
    """
    params = {}
    if task_id:
        query += " AND a.task_id = :task_id"
        params["task_id"] = task_id
    if user_id:
        query += " AND a.user_id = :user_id"
        params["user_id"] = user_id

    result = db.execute(text(query), params)
    rows = result.fetchall()
    columns = result.keys()

    if not rows:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(rows, columns=columns)
