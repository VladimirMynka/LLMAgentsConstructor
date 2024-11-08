from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.user import NotAuthorizedError
from src.db.services import GroupService
from src.db.services.group_provider_service import GroupProviderService
from src.models.graph import GraphModel
from src.models.group import CreateGroupRequestModel, ExpandGroupModel
from src.models.provider import AddProviderToGroupRequestModel, ProviderModel
from src.models.user import UserModel

router = APIRouter(prefix="/groups")


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
        except UserNotInGroupError:
            raise HTTPException(status_code=403, detail="User is not in the group")
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")

    return wrapper


@router.post("/create")
@map_errors
async def create_group(
    body: CreateGroupRequestModel,
    token: str = Depends(get_token),
) -> ExpandGroupModel:
    """
    Create a group.

    Args:
        body: CreateGroupRequestModel - Group name

    Returns:
        LoginResponseModel - User auth token

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return GroupService.create_group(body, token)


@router.get("/{group_id}")
@map_errors
async def get_group_by_id(
    group_id: int,
    token: str = Depends(get_token),
) -> ExpandGroupModel:
    """
    Get group by id.

    Args:
        group_id: int - Group id

    Returns:
        ExpandGroupModel - Group info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupService.get_group_by_id(group_id, token)


@router.get("/{group_id}/owner")
@map_errors
async def get_group_owner(
    group_id: int,
    token: str = Depends(get_token),
) -> UserModel:
    """
    Get group owner.

    Args:
        group_id: int - Group id

    Returns:
        UserModel - User info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupService.get_owner(group_id, token)


@router.get("/{group_id}/graphs")
@map_errors
async def get_graphs(
    group_id: int,
    token: str = Depends(get_token),
) -> list[GraphModel]:
    """
    Get group graphs.

    Args:
        group_id: int - Group id

    Returns:
        list[GraphModel] - List of graphs

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupService.get_graphs(group_id, token)

@router.post("/{group_id}/providers")
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
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
        HTTPException(404): If the provider is not found
    """
    return GroupProviderService.add_provider_to_group(group_id, body, token)
