from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pandas as pd
from fastapi import status

from app.models.user import User, UserRole
from app.models.category import Category
from app.models.task import Task, TaskPriority, TaskStatus
from app.core import security
from app.ml.features import extract_ml_dataset, prepare_single_sample, FEATURE_COLUMNS


def setup_ml_test_data(db):
    admin = User(name="ML Admin", email="ml_admin@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.ADMIN, department="Engineering")
    user = User(name="ML User", email="ml_user@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER, department="Product")
    category = Category(name="ML Test Cat", description="Cat for ML test")

    db.add_all([admin, user, category])
    db.commit()

    admin_token = security.create_access_token(admin.id)
    user_token = security.create_access_token(user.id)

    return admin, admin_token, user, user_token, category


def test_ml_dataset_extraction_prevents_leakage():
    raw_df = pd.DataFrame([
        {
            "task_id": 1,
            "title": "Task 1",
            "user_id": 10,
            "user_name": "Alice",
            "department": "Engineering",
            "category_id": 2,
            "category_name": "Backend",
            "priority": "HIGH",
            "status": "COMPLETED",
            "created_at": "2026-08-01T10:00:00Z",
            "deadline": "2026-08-05T10:00:00Z",
            "completed_at": "2026-08-04T10:00:00Z",
            "estimated_hours": 10.0,
            "actual_hours": 8.0
        }
    ])
    clean_df, stats = extract_ml_dataset(raw_df)
    assert len(clean_df) == 1
    assert "is_late" in clean_df.columns
    assert "completion_days" in clean_df.columns
    # Ensure raw FEATURE_COLUMNS does NOT include post-completion attributes
    assert "completed_at" not in FEATURE_COLUMNS
    assert "actual_hours" not in FEATURE_COLUMNS
    assert "status" not in FEATURE_COLUMNS


def test_ml_health_endpoint(client, db):
    _, admin_token, _, _, _ = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/ml/health", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "models_loaded" in data


def test_predict_overdue_endpoint(client, db):
    _, admin_token, user, user_token, category = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {user_token}"}
    
    payload = {
        "priority": "HIGH",
        "category_id": category.id,
        "user_id": user.id,
        "estimated_hours": 12.0,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    }
    response = client.post("/api/ml/predict-overdue", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "late_probability" in data
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= data["late_probability"] <= 1.0


def test_predict_completion_time_endpoint(client, db):
    _, admin_token, user, user_token, category = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {user_token}"}

    payload = {
        "priority": "HIGH",
        "category_id": category.id,
        "user_id": user.id,
        "estimated_hours": 16.0
    }
    response = client.post("/api/ml/predict-completion-time", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "predicted_completion_days" in data
    assert data["predicted_completion_days"] > 0.0


def test_feature_importance_endpoint(client, db):
    _, admin_token, _, _, _ = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/ml/feature-importance", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "classification_importance" in data
    assert "regression_importance" in data


def test_model_info_endpoint(client, db):
    _, admin_token, _, _, _ = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/ml/model-info", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data


def test_unauthorized_user_prediction_blocked(client, db):
    admin, admin_token, user, user_token, category = setup_ml_test_data(db)
    headers = {"Authorization": f"Bearer {user_token}"}

    # Regular user attempting to request prediction for admin's user_id -> 403 Forbidden
    payload = {
        "priority": "CRITICAL",
        "category_id": category.id,
        "user_id": admin.id,
        "estimated_hours": 20.0
    }
    response = client.post("/api/ml/predict-overdue", json=payload, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
