from fastapi import status
from app.models.user import User, UserRole
from app.models.category import Category
from app.core import security


def create_admin_and_user(db):
    admin = User(
        name="Cat Admin",
        email="cat.admin@example.com",
        password_hash=security.get_password_hash("password123"),
        role=UserRole.ADMIN
    )
    user = User(
        name="Cat Normal",
        email="cat.normal@example.com",
        password_hash=security.get_password_hash("password123"),
        role=UserRole.USER
    )
    db.add_all([admin, user])
    db.commit()
    admin_token = security.create_access_token(admin.id)
    user_token = security.create_access_token(user.id)
    return (admin, admin_token), (user, user_token)


def test_list_categories(client, db):
    (_, _), (_, user_token) = create_admin_and_user(db)
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/api/categories", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_admin_can_create_category(client, db):
    (_, admin_token), (_, _) = create_admin_and_user(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.post(
        "/api/categories",
        json={"name": "Frontend Design", "description": "UI and UX tasks"},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Frontend Design"


def test_duplicate_category_name_fails(client, db):
    (_, admin_token), (_, _) = create_admin_and_user(db)
    headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(
        "/api/categories",
        json={"name": "Backend Ops"},
        headers=headers
    )
    response = client.post(
        "/api/categories",
        json={"name": "Backend Ops"},
        headers=headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_user_cannot_create_category(client, db):
    (_, _), (_, user_token) = create_admin_and_user(db)
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post(
        "/api/categories",
        json={"name": "Forbidden Category"},
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
