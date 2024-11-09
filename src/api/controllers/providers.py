from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.provider import ProviderNotFoundError, UserIsNotProviderOwnerError
from src.db.errors.user import NotAuthorizedError
from src.db.services.provider_service import ProviderService
from src.db.services.provider_token_service import ProviderTokenService
from src.models.provider import (
    CreateProviderRequestModel,
    ExpandProviderModel,
    ProviderModel,
    TestConnectionResponseModel,
    UpdateProviderRequestModel,
)

router = APIRouter(prefix="/providers")


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
        except UserIsNotProviderOwnerError:
            raise HTTPException(
                status_code=403, detail="User is not the owner of the provider"
            )
        except ProviderNotFoundError:
            raise HTTPException(status_code=404, detail="Provider not found")

    return wrapper


@router.post("/")
@map_errors
async def create_provider(
    body: CreateProviderRequestModel,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Create a provider.

    Args:
        body: CreateProviderRequestModel - Provider data

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return ProviderService.create_provider(body, token)


@router.get("/")
@map_errors
async def get_providers(
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Get all providers available for current user.

    Args:
        token: str - User authentication token

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return ProviderService.get_providers(token)


@router.get("/{provider_id}")
@map_errors
async def get_provider_by_id(
    provider_id: int,
    token: str = Depends(get_token),
) -> ExpandProviderModel:
    """
    Get provider by id.

    Args:
        provider_id: int - Provider id

    Returns:
        ExpandProviderModel - Provider info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderService.get_provider_by_id(provider_id, token)


@router.put("/{provider_id}")
@map_errors
async def update_provider(
    provider_id: int,
    body: UpdateProviderRequestModel,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Update provider.

    Args:
        provider_id: int - Provider id
        body: UpdateProviderRequestModel - Provider data

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the provider
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderService.update_provider(provider_id, body, token)


@router.delete("/{provider_id}")
@map_errors
async def delete_provider(
    provider_id: int,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Delete provider.

    Args:
        provider_id: int - Provider id

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the provider
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderService.delete_provider(provider_id, token)


@router.post("/{provider_id}/test_connection")
@map_errors
async def test_connection(
    provider_id: int,
    token: str = Depends(get_token),
) -> TestConnectionResponseModel:
    """
    Test connection to provider.

    Args:
        provider_id: int - Provider id

    Returns:
        TestConnectionResponseModel - Test connection response

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ProviderTokenService.test_connection(provider_id, token)
