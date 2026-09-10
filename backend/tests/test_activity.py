from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.user import User, UserRole
from app.models.category import Category
from app.core import security


def setup_activity_data(db):
    user1 = User(name="Act User 1", email="act1@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER)
    user2 = User(name="Act User 2", email="act2@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER)
    category = Category(name="Act Category")
    db.add_all([user1, user2, category])
    db.commit()

    token1 = security.create_access_token(user1.id)
    token2 = security.create_access_token(user2.id)
    return user1, token1, user2, token2, category


def test_task_creation_and_status_update_logs_activity(client, db):
    user1, token1, _, _, category = setup_activity_data(db)
    headers = {"Authorization": f"Bearer {token1}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    # 1. Create task
    task_res = client.post(
        "/api/tasks",
        json={
            "title": "Activity Logging Task",
            "user_id": user1.id,
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": 4.0
        },
        headers=headers
    )
    task_id = task_res.json()["id"]

    # 2. Status patch
    client.patch(
        f"/api/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers=headers
    )

    # 3. Retrieve activity logs
    act_res = client.get(f"/api/tasks/{task_id}/activity", headers=headers)
    assert act_res.status_code == status.HTTP_200_OK
    activities = act_res.json()
    assert len(activities) >= 2
    types = [a["activity_type"] for a in activities]
    assert "TASK_CREATED" in types
    assert "STATUS_CHANGED" in types


def test_unauthorized_activity_access_fails(client, db):
    user1, token1, user2, token2, category = setup_activity_data(db)
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    task_res = client.post(
        "/api/tasks",
        json={
            "title": "Private Task for User 1",
            "user_id": user1.id,
            "category_id": category.id,
            "deadline": deadline,
            "estimated_hours": 4.0
        },
        headers=headers1
    )
    task_id = task_res.json()["id"]

    # User 2 tries to access User 1's task activity
    act_res = client.get(f"/api/tasks/{task_id}/activity", headers=headers2)
    assert act_res.status_code == status.HTTP_403_FORBIDDEN
