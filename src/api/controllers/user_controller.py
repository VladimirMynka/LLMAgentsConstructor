from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException

from src.db.errors.user import (
    InvalidCredentialsError,
    NotAuthorizedError,
    UserAlreadyExistsError,
    UserHasNoPermissionsError,
    UserNotFoundError,
)
from src.db.services.user_service import UserService
from src.models.group import UserGroupModel
from src.models.user import (
    ChangePasswordRequestModel,
    GetUserByIdRequestModel,
    LoginRequestModel,
    LoginResponseModel,
    LogoutResponseModel,
    PatchUserModel,
    RegisterRequestModel,
    SearchUserRequestModel,
    UserModel,
    UsersModel,
)

router = APIRouter(prefix="/users")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserAlreadyExistsError:
            raise HTTPException(status_code=400, detail="User already exists")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Given token is invalid")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
        except InvalidCredentialsError:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        except UserHasNoPermissionsError:
            raise HTTPException(status_code=403, detail="User has no permissions")

    return wrapper


def get_token(authorization: str = Header(None)):
    """
    Get user auth token from header.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return authorization.split(" ")[1]


@router.post("/login")
@map_errors
async def login(body: LoginRequestModel) -> LoginResponseModel:
    """
    Login a user.

    Args:
        body: LoginRequestModel - User login and password

    Returns:
        LoginResponseModel - User auth token

    Raises:
        HTTPException(401): If the credentials are invalid
    """
    return UserService.login(body)


@router.post("/logout")
@map_errors
async def logout(token: str = Depends(get_token)) -> LogoutResponseModel:
    """
    Logout a user.

    Args:
        token: str - User auth token

    Returns:
        LogoutResponseModel - Logout response

    Raises:
        HTTPException(401): If the token is invalid
    """
    return UserService.logout(token)


@router.post("/register")
@map_errors
async def register(body: RegisterRequestModel) -> LoginResponseModel:
    """
    Register a user.

    Args:
        body: RegisterRequestModel - User login, password and email

    Returns:
        LoginResponseModel - User auth token

    Raises:
        HTTPException(400): If the user already exists
    """
    return UserService.register(body)


@router.get("/me")
@map_errors
async def get_me(token: str = Depends(get_token)) -> UserModel:
    """
    Get user info.

    Args:
        token: str - User auth token

    Returns:
        UserModel - User info

    Raises:
        HTTPException(401): If the token is invalid
    """
    return UserService.get_user_by_auth_token(token)


@router.patch("/me")
@map_errors
async def update_me(
    body: PatchUserModel,
    token: str = Depends(get_token),
) -> UserModel:
    """
    Update user login.

    Args:
        body: PatchUserModel - User login
        token: str - User auth token

    Returns:
        UserModel - User info

    Raises:
        HTTPException(401): If the token is invalid
        HTTPException(400): If the user already exists
    """
    return UserService.patch_user(body, token)


@router.patch("/me/password")
@map_errors
async def update_password(
    body: ChangePasswordRequestModel,
    token: str = Depends(get_token),
) -> UserModel:
    """
    Update user password.

    Args:
        body: ChangePasswordRequestModel - User old and new password
        token: str - User auth token

    Returns:
        UserModel - User info

    Raises:
        HTTPException(401): If the token is invalid
        HTTPException(400): If the credentials are invalid
    """
    return UserService.change_password(body, token)


@router.get("/search")
@map_errors
async def search_users(
    body: SearchUserRequestModel,
    token: str = Depends(get_token),
) -> UsersModel:
    """
    Search users by login.

    Args:
        body: SearchUserRequestModel - User login query
        token: str - User auth token

    Returns:
        UsersModel - Users info

    Raises:
        HTTPException(401): If the token is invalid
    """
    return UserService.search_users_by_login(body, token)


@router.get("/{user_id}")
@map_errors
async def get_user_by_id(
    user_id: GetUserByIdRequestModel,
    token: str = Depends(get_token),
) -> UserModel:
    """
    Get user by id.

    Args:
        user_id: GetUserByIdRequestModel - User id
        token: str - User auth token

    Returns:
        UserModel - User info

    Raises:
        HTTPException(401): If the token is invalid
        HTTPException(404): If the user is not found
    """
    return UserService.get_user_by_id(user_id, token)


@router.get("/{user_id}/groups")
@map_errors
async def get_user_groups(
    user_id: GetUserByIdRequestModel,
    token: str = Depends(get_token),
) -> list[UserGroupModel]:
    """
    Get user groups.

    Args:
        user_id: GetUserByIdRequestModel - User id
        token: str - User auth token

    Returns:
        list[UserGroupModel] - User groups

    Raises:
        HTTPException(401): If the token is invalid
        HTTPException(404): If the user is not found
        HTTPException(403): If the user has no permissions
    """
    return UserService.get_user_groups(user_id, token)
