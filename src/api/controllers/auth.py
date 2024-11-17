from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException

from src.db.errors.user import InvalidCredentialsError, UserAlreadyExistsError
from src.db.services import AuthService
from src.models.user import (
    LoginRequestModel,
    LoginResponseModel,
    LogoutResponseModel,
    RegisterRequestModel,
)

router = APIRouter(prefix="/auth")


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
        except InvalidCredentialsError:
            raise HTTPException(status_code=401, detail="Invalid credentials")

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
    return AuthService.login(body)


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
    return AuthService.logout(token)


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
    return AuthService.register(body)
