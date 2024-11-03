from unittest.mock import AsyncMock, patch

import pytest

from src.api.controllers.user_controller import router
from src.db.services.user_service import UserService


@pytest.fixture
def client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_user_service():
    with patch.object(
        UserService, "login", new_callable=AsyncMock
    ) as mock_login, patch.object(
        UserService, "logout", new_callable=AsyncMock
    ) as mock_logout, patch.object(
        UserService, "register", new_callable=AsyncMock
    ) as mock_register, patch.object(
        UserService, "get_user_by_auth_token", new_callable=AsyncMock
    ) as mock_get_user_by_auth_token, patch.object(
        UserService, "patch_user", new_callable=AsyncMock
    ) as mock_patch_user, patch.object(
        UserService, "change_password", new_callable=AsyncMock
    ) as mock_change_password, patch.object(
        UserService, "search_users_by_login", new_callable=AsyncMock
    ) as mock_search_users_by_login, patch.object(
        UserService, "get_user_by_id", new_callable=AsyncMock
    ) as mock_get_user_by_id, patch.object(
        UserService, "get_user_groups", new_callable=AsyncMock
    ) as mock_get_user_groups:
        yield {
            "login": mock_login,
            "logout": mock_logout,
            "register": mock_register,
            "get_user_by_auth_token": mock_get_user_by_auth_token,
            "patch_user": mock_patch_user,
            "change_password": mock_change_password,
            "search_users_by_login": mock_search_users_by_login,
            "get_user_by_id": mock_get_user_by_id,
            "get_user_groups": mock_get_user_groups,
        }
