from fastapi import status
from app.models.user import User, UserRole
from app.core import security


def create_test_user(db, email, role=UserRole.USER, name="Test User"):
    user = User(
        name=name,
        email=email,
        password_hash=security.get_password_hash("password123"),
        role=role,
        department="Testing"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = security.create_access_token(user.id)
    return user, token


def test_admin_can_list_users(client, db):
    admin, admin_token = create_test_user(db, "admin.list@example.com", role=UserRole.ADMIN, name="Admin")
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/api/users", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


def test_user_cannot_list_users(client, db):
    user, token = create_test_user(db, "normal.list@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/users", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_can_get_assignable_users(client, db):
    user, token = create_test_user(db, "normal.assignable@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/users/assignable", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data


def test_user_can_get_own_profile(client, db):
    user, token = create_test_user(db, "own.profile@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "own.profile@example.com"


def test_user_cannot_get_other_user_profile(client, db):
    user1, token1 = create_test_user(db, "user1.prof@example.com", role=UserRole.USER)
    user2, token2 = create_test_user(db, "user2.prof@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {token1}"}

    response = client.get(f"/api/users/{user2.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_cannot_promote_self_to_admin(client, db):
    user, token = create_test_user(db, "promote.self@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(
        f"/api/users/{user.id}",
        json={"role": "ADMIN"},
        headers=headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_delete_user(client, db):
    admin, admin_token = create_test_user(db, "admin.del@example.com", role=UserRole.ADMIN)
    target, _ = create_test_user(db, "target.del@example.com", role=UserRole.USER)
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/api/users/{target.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
