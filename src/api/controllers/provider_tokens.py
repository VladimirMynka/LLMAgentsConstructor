from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.provider import ProviderNotFoundError, UserIsNotProviderOwnerError
from src.db.errors.user import NotAuthorizedError
from src.db.services.provider_token_service import ProviderTokenService
from src.models.provider import ProviderModel
from src.models.provider_token import CreateProviderTokenRequestModel

router = APIRouter(prefix="/{provider_id}/tokens")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except ProviderNotFoundError:
            raise HTTPException(status_code=404, detail="Provider not found")

    return wrapper


@router.put("/")
@map_errors
async def add_provider_token(
    body: CreateProviderTokenRequestModel,
    provider_id: int,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Add or update provider token.

    Args:
        body: CreateProviderTokenRequestModel - Provider token data
        provider_id: int - Provider id

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderTokenService.add_provider_token(body, provider_id, token)


@router.delete("/")
@map_errors
async def delete_provider_token(
    provider_id: int,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Delete provider token.

    Args:
        provider_id: int - Provider id

    Returns:
        list[ProviderModel] - List of providers after deletion

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderTokenService.delete_provider_token(provider_id, token)
