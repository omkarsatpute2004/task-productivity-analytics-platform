from datetime import datetime, timedelta, timezone
from fastapi import status
from app.models.user import User, UserRole
from app.models.category import Category
from app.core import security


def setup_filtering_data(db):
    admin = User(name="Filt Admin", email="fadmin@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.ADMIN)
    user1 = User(name="Filt User 1", email="fuser1@example.com", password_hash=security.get_password_hash("pw"), role=UserRole.USER)
    category = Category(name="Filt Category")
    db.add_all([admin, user1, category])
    db.commit()

    admin_token = security.create_access_token(admin.id)
    user1_token = security.create_access_token(user1.id)
    return admin, admin_token, user1, user1_token, category


def test_task_search_and_filtering(client, db):
    admin, admin_token, user1, user1_token, category = setup_filtering_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}
    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    # Create task A (HIGH priority, TODO)
    client.post(
        "/api/tasks",
        json={
            "title": "Alpha Search Target",
            "description": "Unique alpha task description",
            "user_id": user1.id,
            "category_id": category.id,
            "priority": "HIGH",
            "status": "TODO",
            "deadline": deadline,
            "estimated_hours": 2.0
        },
        headers=headers
    )

    # Create task B (LOW priority, COMPLETED)
    client.post(
        "/api/tasks",
        json={
            "title": "Beta Search Target",
            "description": "Unique beta task description",
            "user_id": user1.id,
            "category_id": category.id,
            "priority": "LOW",
            "status": "COMPLETED",
            "deadline": deadline,
            "estimated_hours": 4.0
        },
        headers=headers
    )

    # 1. Search text filter
    res_search = client.get("/api/tasks?search=Alpha", headers=headers)
    assert res_search.status_code == status.HTTP_200_OK
    data_search = res_search.json()
    assert data_search["total"] == 1
    assert data_search["items"][0]["title"] == "Alpha Search Target"

    # 2. Priority & Status filter
    res_filter = client.get("/api/tasks?priority=HIGH&status=TODO", headers=headers)
    assert res_filter.status_code == status.HTTP_200_OK
    data_filter = res_filter.json()
    assert data_filter["total"] == 1
    assert data_filter["items"][0]["priority"] == "HIGH"


def test_pagination_metadata(client, db):
    _, _, user1, user1_token, category = setup_filtering_data(db)
    headers = {"Authorization": f"Bearer {user1_token}"}
    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    # Create 5 tasks
    for i in range(5):
        client.post(
            "/api/tasks",
            json={
                "title": f"Paginated Task #{i+1}",
                "user_id": user1.id,
                "category_id": category.id,
                "deadline": deadline,
                "estimated_hours": 1.0
            },
            headers=headers
        )

    res_page = client.get("/api/tasks?page=1&limit=2", headers=headers)
    assert res_page.status_code == status.HTTP_200_OK
    data_page = res_page.json()
    assert len(data_page["items"]) == 2
    assert data_page["page"] == 1
    assert data_page["limit"] == 2
    assert data_page["total"] >= 5
    assert data_page["pages"] >= 3
