from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.provider import ProviderAlreadyInGroupError, ProviderNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.group_provider_service import GroupProviderService
from src.models.provider import AddProviderToGroupRequestModel, ProviderModel

router = APIRouter(prefix="/{group_id}/providers")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ProviderAlreadyInGroupError:
            raise HTTPException(status_code=400, detail="Provider already in the group")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except UserNotInGroupError:
            raise HTTPException(status_code=404, detail="Group not found")
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")
        except ProviderNotFoundError:
            raise HTTPException(status_code=404, detail="Provider not found")

    return wrapper


@router.post("/")
@map_errors
async def add_provider_to_group(
    group_id: int,
    body: AddProviderToGroupRequestModel,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Add provider to group.

    Args:
        group_id: int - Group id
        body: AddProviderToGroupRequestModel - Add provider to group request model

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(400): If the provider is already in the group
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
        HTTPException(404): If the provider is not found
    """
    return GroupProviderService.add_group_provider(body, group_id, token)


@router.get("/")
@map_errors
async def get_group_providers(
    group_id: int,
    token: str = Depends(get_token),
) -> list[ProviderModel]:
    """
    Get group providers.

    Args:
        group_id: int - Group id

    Returns:
        list[ProviderModel] - List of providers

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupProviderService.get_group_providers(group_id, token)
