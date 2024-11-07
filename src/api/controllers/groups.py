from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException

from src.api.controllers.users import get_token
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
from src.db.services import GroupService
from src.db.services.member_service import MemberService
from src.models.graph import GraphModel
from src.models.group import (
    AddMemberRequestModel,
    CreateGroupRequestModel,
    ExpandGroupModel,
    GroupPermissionsModel,
    MemberModel,
    UserGroupModel,
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
        except HaraKiriForbiddenError:
            raise HTTPException(status_code=400, detail="Hara-kiri is forbidden")
        except UserAlreadyInGroupError:
            raise HTTPException(status_code=400, detail="Member already in the group")
        except GroupAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Group already exists")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except UserHasNoPermissionsError:
            raise HTTPException(status_code=403, detail="Member has no permissions")
        except UserNotInGroupError:
            raise HTTPException(status_code=403, detail="User is not in the group")
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="Member not found")

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
    return GroupService.get_owner(group_id, token)


@router.get("/{group_id}/members")
@map_errors
async def get_members(
    group_id: int,
    token: str = Depends(get_token),
) -> list[MemberModel]:
    """
    Get group members.

    Args:
        group_id: int - Group id

    Returns:
        list[UserModel] - List of users

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(404): If the group is not found
        HTTPException(403): If the requester is not in the group
    """
    return GroupService.get_members(group_id, token)


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
        HTTPException(404): If the group is not found
        HTTPException(403): If the requester is not in the group
    """
    return GroupService.get_graphs(group_id, token)


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
    return MemberService.leave_group(group_id, token)


@router.get("/{group_id}/members/{member_id}")
@map_errors
async def get_member_info(
    group_id: int,
    member_id: int,
    token: str = Depends(get_token),
) -> MemberModel:
    """
    Get group member info.

    Args:
        group_id: int - Group id
        member_id: int - Member id

    Returns:
        MemberModel - Member info

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404, detail="Group not found"): If the group is not found
        HTTPException(404, detail="Member is not in the group"): If the member is not in the group
    """
    return MemberService.get_member(group_id, member_id, token)


@router.patch("/{group_id}/members/{member_id}")
@map_errors
async def update_member_info(
    group_id: int,
    member_id: int,
    body: GroupPermissionsModel,
    token: str = Depends(get_token),
) -> list[MemberModel]:
    """
    Update group member info.

    Args:
        group_id: int - Group id
        member_id: int - Member id
        body: GroupPermissionsModel - Group permissions model

    Returns:
        list[MemberModel] - List of members

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(404): If the group is not found
        HTTPException(403): If the requester is not in the group or has no permissions to edit users permissions
    """
    return MemberService.update_member(group_id, member_id, body, token)


@router.delete("/{group_id}/members/{member_id}")
@map_errors
async def delete_member(
    group_id: int,
    member_id: int,
    token: str = Depends(get_token),
) -> list[MemberModel]:
    """
    Delete group member.

    Args:
        group_id: int - Group id
        member_id: int - Member id

    Returns:
        list[MemberModel] - List of members

    Raises:
        HTTPException(400, detail="Hara-kiri is forbidden"): If the user is the owner of the group
        HTTPException(401): If the requester is not authorized
        HTTPException(404): If the group is not found
        HTTPException(403): If the requester is not in the group or has no permissions to delete users
    """
    return MemberService.delete_member(group_id, member_id, token)


@router.post("/{group_id}/members")
@map_errors
async def add_member(
    group_id: int,
    body: AddMemberRequestModel,
    token: str = Depends(get_token),
) -> list[MemberModel]:
    """
    Add a member to a group.

    Args:
        group_id: int - Group id
        body: AddMemberRequestModel - Member info

    Returns:
        list[MemberModel] - List of members

    Raises:
        HTTPException(400, detail="Member already in the group"): If the user is already in the group
        HTTPException(401): If the requester is not authorized
        HTTPException(404): If the group is not found
        HTTPException(403): If the requester is not in the group or has no permissions to add users
    """
    return MemberService.add_member(body, group_id, token)
