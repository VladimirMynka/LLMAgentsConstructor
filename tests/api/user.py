import pytest
from fastapi.testclient import TestClient

from src.api.controllers.user_controller import router

client = TestClient(router)


@pytest.fixture
def token():
    return "Bearer test_token"


def test_login():
    response = client.post(
        "/users/login", json={"login": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    assert "auth_token" in response.json()


def test_logout(token):
    response = client.post("/users/logout", headers={"Authorization": token})
    assert response.status_code == 200
    assert response.json() == {"detail": "Successfully logged out"}


def test_register():
    response = client.post(
        "/users/register",
        json={
            "login": "new_user",
            "password": "new_password",
            "email": "new_user@example.com",
        },
    )
    assert response.status_code == 200
    assert "auth_token" in response.json()


def test_get_me(token):
    response = client.get("/users/me", headers={"Authorization": token})
    assert response.status_code == 200
    assert "login" in response.json()


def test_update_me(token):
    response = client.patch(
        "/users/me", headers={"Authorization": token}, json={"login": "updated_user"}
    )
    assert response.status_code == 200
    assert response.json()["login"] == "updated_user"


def test_update_password(token):
    response = client.patch(
        "/users/me/password",
        headers={"Authorization": token},
        json={"old_password": "old_password", "new_password": "new_password"},
    )
    assert response.status_code == 200
    assert "login" in response.json()


def test_search_users(token):
    response = client.get(
        "/users/search", headers={"Authorization": token}, json={"query": "test"}
    )
    assert response.status_code == 200
    assert isinstance(response.json()["users"], list)


def test_get_user_by_id(token):
    response = client.get("/users/1", headers={"Authorization": token})
    assert response.status_code == 200
    assert "login" in response.json()


def test_get_user_groups(token):
    response = client.get("/users/1/groups", headers={"Authorization": token})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
