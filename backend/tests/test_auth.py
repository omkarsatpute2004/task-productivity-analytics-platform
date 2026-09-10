from datetime import timedelta
from fastapi import status
from app.core import security


def test_register_user_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New Registered User",
            "email": "new.registered@example.com",
            "password": "secure-password123",
            "department": "Engineering"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Registered User"
    assert data["email"] == "new.registered@example.com"
    assert data["role"] == "USER"
    assert "password_hash" not in data


def test_register_duplicate_email_fails(client):
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "name": "User One",
            "email": "duplicate.test@example.com",
            "password": "password123"
        }
    )
    # Duplicate registration
    response = client.post(
        "/api/auth/register",
        json={
            "name": "User Two",
            "email": "duplicate.test@example.com",
            "password": "password456"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"]


def test_login_success(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={
            "name": "Login User",
            "email": "login.test@example.com",
            "password": "mysecretpassword"
        }
    )
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login.test@example.com",
            "password": "mysecretpassword"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login.test@example.com"
    assert "password_hash" not in data["user"]


def test_login_invalid_password_fails(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Login Fail User",
            "email": "login.fail@example.com",
            "password": "correctpassword"
        }
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login.fail@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials."


def test_get_me_with_valid_token(client):
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Me User",
            "email": "get.me@example.com",
            "password": "mepassword123"
        }
    )
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": "get.me@example.com",
            "password": "mepassword123"
        }
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "get.me@example.com"


def test_get_me_without_token_fails(client):
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token_fails(client):
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Expired User",
            "email": "expired@example.com",
            "password": "password123"
        }
    )
    user_id = reg_res.json()["id"]

    # Generate expired token
    expired_token = security.create_access_token(
        subject=user_id,
        expires_delta=timedelta(seconds=-10)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}

    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
