from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException

from src.api.controllers.user_controller import get_token
from src.db.errors.group import (
    GroupAlreadyExistsError,
    GroupNotFoundError,
    HaraKiriForbiddenError,
    UserAlreadyInGroupError,
    UserNotInGroupError,
)
from src.db.errors.user import (
    InvalidCredentialsError,
    NotAuthorizedError,
    UserAlreadyExistsError,
    UserHasNoPermissionsError,
    UserNotFoundError,
)
from src.db.services.group_service import GroupService
from src.models.group import CreateGroupRequestModel, ExpandGroupModel, UserGroupModel
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
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")
        except UserNotInGroupError:
            raise HTTPException(status_code=403, detail="User is not in the group")
        except HaraKiriForbiddenError:
            raise HTTPException(status_code=400, detail="Hara-kiri is forbidden")
        except UserHasNoPermissionsError:
            raise HTTPException(status_code=403, detail="User has no permissions")
        except UserAlreadyInGroupError:
            raise HTTPException(status_code=400, detail="User already in the group")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except GroupAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Group already exists")

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
        HTTPException(404): If the group is not found
        HTTPException(403): If the user is not in the group
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
        HTTPException(404): If the group is not found
        HTTPException(403): If the user is not in the group
    """
    return GroupService.get_group_owner(group_id, token)


@router.post("/{group_id}/leave")
@map_errors
async def leave_group(
    group_id: int,
    token: str = Depends(get_token),
) -> None:
    """
    Leave a group.

    Args:
        group_id: int - Group id

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the group is not found
        HTTPException(403): If the user is not in the group
    """
    return GroupService.leave_group(group_id, token)
