from fastapi import status


def test_health_endpoint(client):
    """Test /api/health returns HTTP 200 and expected payload."""
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "task-productivity-platform"


def test_db_health_endpoint(client):
    """Test /api/health/db returns HTTP 200 when database connection is live."""
    response = client.get("/api/health/db")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert data["service"] == "task-productivity-platform"
