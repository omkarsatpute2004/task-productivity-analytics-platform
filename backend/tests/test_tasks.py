from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import status
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.task import TaskPriority, TaskStatus
from app.core import security


def setup_task_test_data(db):
    admin = User(name="Task Admin", email="tadmin@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.ADMIN)
    user1 = User(name="Task User 1", email="tuser1@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER)
    user2 = User(name="Task User 2", email="tuser2@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER)
    category = Category(name="Dev Task Cat", description="Task category")

    db.add_all([admin, user1, user2, category])
    db.commit()

    admin_token = security.create_access_token(admin.id)
    user1_token = security.create_access_token(user1.id)
    user2_token = security.create_access_token(user2.id)

    return admin, admin_token, user1, user1_token, user2, user2_token, category


def test_user_can_create_own_task(client, db):
    _, _, user1, user1_token, _, _, category = setup_task_test_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = client.post(
        "/api/tasks",
        json={
            "title": "Build Auth Layer",
            "description": "Implement JWT endpoints",
            "user_id": user1.id,
            "category_id": category.id,
            "priority": "HIGH",
            "status": "TODO",
            "deadline": deadline,
            "estimated_hours": 12.5,
            "actual_hours": 0.0
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Build Auth Layer"
    assert data["user_id"] == user1.id
    assert data["status"] == "TODO"


def test_user_cannot_assign_task_to_other_fails(client, db):
    _, _, user1, user1_token, user2, _, category = setup_task_test_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = client.post(
        "/api/tasks",
        json={
            "title": "Unauthorized Assignment",
            "user_id": user2.id,  # Trying to assign to user2
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": 5.0
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_assign_task_to_any_user(client, db):
    admin, admin_token, _, _, user2, _, category = setup_task_test_data(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = client.post(
        "/api/tasks",
        json={
            "title": "Admin Assigned Task",
            "user_id": user2.id,
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": 8.0
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["user_id"] == user2.id


def test_update_task_status_completes_task_and_reopening_resets_completed_at(client, db):
    _, _, user1, user1_token, _, _, category = setup_task_test_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    create_res = client.post(
        "/api/tasks",
        json={
            "title": "Status Patch Lifecycle Task",
            "user_id": user1.id,
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": 10.0
        },
        headers=headers
    )
    task_id = create_res.json()["id"]

    # Patch to COMPLETED
    patch_res = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": "COMPLETED"},
        headers=headers
    )
    assert patch_res.status_code == status.HTTP_200_OK
    data = patch_res.json()
    assert data["status"] == "COMPLETED"
    assert data["completed_at"] is not None

    # Reopen task to IN_PROGRESS
    reopen_res = client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=headers
    )
    assert reopen_res.status_code == status.HTTP_200_OK
    reopen_data = reopen_res.json()
    assert reopen_data["status"] == "IN_PROGRESS"
    assert reopen_data["completed_at"] is None


def test_invalid_task_hours_validation_fails(client, db):
    _, _, user1, user1_token, _, _, category = setup_task_test_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = client.post(
        "/api/tasks",
        json={
            "title": "Negative Hours Task",
            "user_id": user1.id,
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": -5.0  # Invalid negative hours
        },
        headers=headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
