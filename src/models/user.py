from dataclasses import Field

from openai import BaseModel


class RegisterRequestModel(BaseModel):
    """
    Register request model.
    """

    username: str = Field(..., description="User login")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {
                "username": "VladimirMynka",
                "password": "strongpassword123",
            }
        }


class UserModel(BaseModel):
    """
    User model.
    """

    id: int = Field(..., description="User id")
    login: str = Field(..., description="User login")

    class Config:
        schema_extra = {
            "example": {"id": 1, "login": "VladimirMynka"},
        }


class UsersModel(BaseModel):
    """
    Users model.
    """

    users: list[UserModel] = Field(..., description="List of users")

    class Config:
        schema_extra = {
            "example": {
                "users": [UserModel.Config.schema_extra["example"]],
            }
        }


class LoginRequestModel(BaseModel):
    """
    Login request model.
    """

    username: str = Field(..., description="User login")
    password: str = Field(..., description="User password")

    class Config:
        schema_extra = {
            "example": {
                "username": "VladimirMynka",
                "password": "strongpassword123",
            }
        }


class LoginResponseModel(BaseModel):
    """
    Login response model.
    """

    id: int = Field(..., description="User id")
    auth_token: str = Field(..., description="User auth token")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "auth_token": "a3f5b7c9d1e2f4a6",
            }
        }


class LogoutResponseModel(BaseModel):
    """
    Logout response model.
    """

    message: str = Field(..., description="Logout message")

    class Config:
        schema_extra = {
            "example": {"message": "Success"},
        }


class SearchUserRequestModel(BaseModel):
    """
    Search user request model.
    """

    query: str = Field(..., description="Search query")

    class Config:
        schema_extra = {
            "example": {"query": "Vl"},
        }


class PatchUserModel(BaseModel):
    """
    Patch user model.
    """

    new_login: str = Field(..., description="New user login")

    class Config:
        schema_extra = {
            "example": {"new_login": "VladimirMynka2"},
        }


class ChangePasswordRequestModel(BaseModel):
    """
    Change password request model.
    """

    old_password: str = Field(..., description="Old user password")
    new_password: str = Field(..., description="New user password")

    class Config:
        schema_extra = {
            "example": {
                "old_password": "strongpassword123",
                "new_password": "strongpassword456",
            },
        }


class GetUserByIdRequestModel(BaseModel):
    """
    Get user by id request model.
    """

    user_id: int = Field(..., description="User id")

    class Config:
        schema_extra = {
            "example": {"user_id": 1},
        }


class UserDetailsModel(BaseModel):
    """
    User details model.
    """

    groups_ids: list[int] | None = Field(..., description="List of user groups ids")

    class Config:
        schema_extra = {
            "example": {"groups_ids": [1, 2, 3]},
        }


class ExpandedUserModel(BaseModel):
    """
    Expanded user model.
    """

    user_id: int = Field(..., description="User id")
    login: str = Field(..., description="User login")
    details: UserDetailsModel = Field(..., description="User details")

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "login": "VladimirMynka",
                "details": UserDetailsModel.Config.schema_extra["example"],
            }
        }
