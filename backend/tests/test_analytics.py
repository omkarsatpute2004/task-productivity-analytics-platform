from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pandas as pd
from fastapi import status

from app.models.user import User, UserRole
from app.models.category import Category
from app.models.task import Task, TaskPriority, TaskStatus
from app.core import security
from app.analytics.cleaning import clean_tasks_dataframe
from app.analytics.features import enrich_task_features
from app.analytics.statistics import calculate_descriptive_stats, calculate_correlations, detect_outliers_iqr


def setup_analytics_test_data(db):
    admin = User(name="Analytics Admin", email="an_admin@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.ADMIN, department="Engineering")
    user = User(name="Analytics User", email="an_user@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER, department="Product")
    category = Category(name="Analytics Cat", description="Cat for analytics test")

    db.add_all([admin, user, category])
    db.commit()

    now = datetime.now(timezone.utc)
    task1 = Task(
        title="Completed On-Time Task",
        user_id=user.id,
        category_id=category.id,
        priority=TaskPriority.HIGH,
        status=TaskStatus.COMPLETED,
        deadline=now + timedelta(days=5),
        completed_at=now + timedelta(days=2),
        estimated_hours=Decimal("10.00"),
        actual_hours=Decimal("8.00")
    )
    task2 = Task(
        title="Overdue Incomplete Task",
        user_id=user.id,
        category_id=category.id,
        priority=TaskPriority.CRITICAL,
        status=TaskStatus.TODO,
        deadline=now - timedelta(days=2),
        estimated_hours=Decimal("15.00"),
        actual_hours=Decimal("0.00")
    )

    db.add_all([task1, task2])
    db.commit()

    admin_token = security.create_access_token(admin.id)
    user_token = security.create_access_token(user.id)

    return admin, admin_token, user, user_token, category


def test_analytics_summary_unauthenticated(client):
    response = client.get("/api/analytics/summary")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_analytics_summary_authenticated(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/summary", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_tasks" in data
    assert "completion_rate" in data
    assert "overdue_tasks" in data
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["overdue_tasks"] == 1


def test_status_distribution_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/status-distribution", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    statuses = [item["status"] for item in data]
    assert "COMPLETED" in statuses
    assert "TODO" in statuses


def test_priority_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/priority", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    priorities = [item["priority"] for item in data]
    assert "HIGH" in priorities
    assert "CRITICAL" in priorities


def test_categories_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/categories", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["category_name"] == "Analytics Cat"


def test_users_productivity_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/users", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_departments_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/departments", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_completion_trend_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/completion-trend?interval=daily", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_overdue_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/overdue", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_overdue" in data
    assert data["total_overdue"] == 1


def test_workload_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/workload", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_estimation_analysis_endpoint(client, db):
    _, admin_token, _, _, _ = setup_analytics_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/analytics/estimation", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_estimated_hours" in data
    assert "statistics" in data
    assert "estimated_hours" in data["statistics"]


def test_data_cleaning_unit():
    raw_data = pd.DataFrame([
        {"task_id": 1, "estimated_hours": -5.0, "actual_hours": 10.0, "status": "TODO"},
        {"task_id": 1, "estimated_hours": -5.0, "actual_hours": 10.0, "status": "TODO"}, # duplicate
        {"task_id": 2, "estimated_hours": 8.0, "actual_hours": -2.0, "status": "COMPLETED"}
    ])
    clean_df, meta = clean_tasks_dataframe(raw_data)
    assert meta["duplicates_removed"] == 1
    assert meta["invalid_hours_fixed"] == 2
    assert pd.isna(clean_df.loc[clean_df["task_id"] == 1, "estimated_hours"].values[0])
    assert pd.isna(clean_df.loc[clean_df["task_id"] == 2, "actual_hours"].values[0])


def test_feature_engineering_unit():
    now = pd.Timestamp(datetime.now(timezone.utc))
    df = pd.DataFrame([
        {
            "task_id": 1,
            "status": "COMPLETED",
            "created_at": now - pd.Timedelta(days=2),
            "completed_at": now,
            "deadline": now + pd.Timedelta(days=1),
            "estimated_hours": 10.0,
            "actual_hours": 12.0
        }
    ])
    df_enriched = enrich_task_features(df)
    assert df_enriched["is_completed"].values[0] == True
    assert df_enriched["is_on_time"].values[0] == True
    assert df_enriched["is_overdue"].values[0] == False
    assert df_enriched["estimation_error"].values[0] == 2.0


def test_statistical_calculations_unit():
    series = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0, 1000.0]) # 1000 is an outlier
    stats = calculate_descriptive_stats(series)
    assert stats["count"] == 6
    assert stats["median"] == 35.0

    outliers = detect_outliers_iqr(series)
    assert outliers["outlier_count"] == 1
    assert 1000.0 in outliers["outliers"]


def test_completed_task_with_null_actual_hours_regression(client, db):
    """
    Regression Test for NULL actual_hours bug:
    Verify that a completed task with estimated_hours populated but actual_hours = NULL
    does not crash the analytics feature enrichment or endpoints (HTTP 200),
    and leaves estimation_error as NaN/None without fake values.
    """
    now = datetime.now(timezone.utc)
    user = User(name="Null Hours User", email="null_hours@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER, department="Testing")
    category = Category(name="Null Hours Cat", description="Cat for null hours regression test")
    db.add_all([user, category])
    db.commit()

    task_null_actual = Task(
        title="Completed Task Null Actual Hours",
        user_id=user.id,
        category_id=category.id,
        priority=TaskPriority.HIGH,
        status=TaskStatus.COMPLETED,
        deadline=now + timedelta(days=5),
        completed_at=now + timedelta(days=1),
        estimated_hours=Decimal("14.00"),
        actual_hours=None  # NULL actual_hours
    )
    db.add(task_null_actual)
    db.commit()

    # Unit test verify enrich_task_features does not crash
    df_raw = pd.DataFrame([{
        "task_id": task_null_actual.id,
        "status": "COMPLETED",
        "created_at": pd.Timestamp(now),
        "completed_at": pd.Timestamp(now + timedelta(days=1)),
        "deadline": pd.Timestamp(now + timedelta(days=5)),
        "estimated_hours": 14.0,
        "actual_hours": None
    }])
    df_enriched = enrich_task_features(df_raw)
    assert pd.isna(df_enriched.loc[0, "estimation_error"])
    assert pd.isna(df_enriched.loc[0, "estimation_error_percentage"])

    # API endpoint verify HTTP 200
    user_token = security.create_access_token(user.id)
    headers = {"Authorization": f"Bearer {user_token}"}
    for endpoint in ["/api/analytics/summary", "/api/analytics/status-distribution", "/api/analytics/categories", "/api/analytics/estimation"]:
        res = client.get(endpoint, headers=headers)
        assert res.status_code == status.HTTP_200_OK

