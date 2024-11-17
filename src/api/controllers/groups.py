from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.user import NotAuthorizedError
from src.db.services import GroupService
from src.models.group import (
    CreateGroupRequestModel,
    DeleteGroupResponseModel,
    ExpandGroupModel,
    GroupModel,
    UpdateGroupRequestModel,
)
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


@router.get("/")
@map_errors
async def get_groups(
    token: str = Depends(get_token),
) -> list[GroupModel]:
    """
    Get all groups of current user.

    Returns:
        list[GroupModel] - List of group models

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return GroupService.get_groups(token)


@router.post("/")
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
        ExpandGroupModel - Expand group model

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


@router.patch("/{group_id}")
@map_errors
async def update_group(
    group_id: int,
    body: UpdateGroupRequestModel,
    token: str = Depends(get_token),
) -> ExpandGroupModel:
    """
    Update group.

    Args:
        group_id: int - Group id
        body: UpdateGroupRequestModel - Group name

    Returns:
        ExpandGroupModel - Expand group model

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not in the group or does not have permissions
        HTTPException(404): If the group is not found
    """
    return GroupService.update_group(body, group_id, token)


@router.delete("/{group_id}")
@map_errors
async def delete_group(
    group_id: int,
    token: str = Depends(get_token),
) -> DeleteGroupResponseModel:
    """
    Delete group.

    Args:
        group_id: int - Group id

    Returns:
        DeleteGroupResponseModel - Delete group response model

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not in the group or does not have permissions
        HTTPException(404): If the group is not found
    """
    return GroupService.delete_group(group_id, token)


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
