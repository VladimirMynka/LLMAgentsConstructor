from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities import Group
from src.db.entities.user_group import UserGroup
from src.db.errors.group import (
    HaraKiriForbiddenError,
    UserAlreadyInGroupError,
    UserNotInGroupError,
)
from src.db.errors.user import UserHasNoPermissionsError, UserNotFoundError
from src.db.services.group_service import GroupService
from src.db.services.user_service import UserService
from src.models.group import (
    AddMemberRequestModel,
    GroupPermissionsModel,
    MemberModel,
    UserGroupModel,
)
from src.models.user import UserModel


class MemberService:
    """
    Group of methods for managing group members.
    """

    @classmethod
    @use_repository
    def get_member(
        cls,
        group_id: int,
        member_id: int,
        auth_token: str,
        repository: Session,
    ) -> MemberModel:
        """
        Get group member info.

        Args:
            group_id: int - Group id
            member_id: int - Member id
            auth_token: str - Auth token

        Returns:
            MemberModel - Member info

        Raises:
            NotAuthorizedError: Requester not authorized
            UserNotInGroupError: Requester is not in the group
            GroupNotFoundError: Group not found
            UserNotFoundError: Requester is not in the group
        """
        requester = UserService.get_user_by_token(auth_token)
        cls._check_user_in_group(requester.id, group_id, repository)
        member = repository.get(UserGroup, member_id, group_id)
        if not member:
            raise UserNotFoundError("Member is not in the group")
        return member

    @classmethod
    @use_repository
    def add_member(
        cls,
        data: AddMemberRequestModel,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[MemberModel]:
        """
        Add group member.

        Args:
            data: AddMemberRequestModel - Add member request model
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            list[MemberModel] - List of group members

        Raises:
            NotAuthorizedError: Requester not authorized
            UserNotInGroupError: Requester is not in the group
            UserHasNoPermissionsError: Requester has no permissions
            UserAlreadyInGroupError: User is already in the group
        """
        adder_model: UserModel = UserService.get_user_by_auth_token(auth_token)
        adder: UserGroup = cls.check_user_in_group(adder_model.id, group_id, repository)

        cls.check_permissions(adder, "change_members")  # raise if no permissions

        new_member = repository.get(UserGroup, data.user_id, group_id)
        if new_member:
            raise UserAlreadyInGroupError("User is already in the group.")

        if data.permissions.owner:
            cls._transfer_ownership_if_needed(adder, data.user_id, group_id, repository)

        new_user_group = UserGroup(
            user_id=data.user_id,
            group_id=group_id,
            **cls._calculate_add_permissions(data.permissions, adder),
        )

        repository.add(new_user_group)
        repository.commit()

        return GroupService.get_group_members(group_id)

    @classmethod
    def get_members(
        cls,
        group_id: int,
        auth_token: str,
    ) -> list[MemberModel]:
        """
        Get group members.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            list[MemberModel] - List of group members

        Raises:
            NotAuthorizedError: User not authorized
            GroupNotFoundError: Group not found
            UserNotInGroupError: User is not in the group
        """
        group = GroupService.get_group_by_id(group_id, auth_token)
        return group.members

    @classmethod
    @use_repository
    def update_member(
        cls,
        data: GroupPermissionsModel,
        group_id: int,
        member_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[MemberModel]:
        """
        Update group member.

        Args:
            data: GroupPermissionsModel - Group permissions model
            group_id: int - Group id
            member_id: int - Member id
            auth_token: str - Auth token

        Returns:
            list[MemberModel] - List of group members

        Raises:
            NotAuthorizedError: Requester not authorized
            UserNotInGroupError: Requester is not in the group
            UserHasNoPermissionsError: Requester has no permissions to edit users permissions
            UserNotFoundError: Member is not in the group
        """
        updater_model = UserService.get_user_by_token(auth_token)

        updater = cls.check_user_in_group(updater_model.id, group_id, repository)

        cls.check_permissions(updater, "change_members")

        cls._transfer_ownership_if_needed(updater, member_id, group_id, repository)

        updating_member = cls.check_user_in_group(
            member_id, group_id, repository, "Updating member is not in the group"
        )

        cls._apply_update_permissions(data, updating_member, updater)

        repository.commit()

        return GroupService.get_group_members(group_id)

    @classmethod
    @use_repository
    def delete_member(
        cls, group_id: int, member_id: int, auth_token: str, repository: Session
    ) -> list[MemberModel]:
        """
        Delete group member.

        Args:
            group_id: int - Group id
            member_id: int - Member id
            auth_token: str - Auth token

        Returns:
            list[MemberModel] - List of group members

        Raises:
            NotAuthorizedError: Requester not authorized
            UserNotInGroupError: Requester is not in the group
            UserHasNoPermissionsError: Requester has no permissions to delete users from the group
            HaraKiriForbiddenError: Requester is the owner of the group
        """
        remover = UserService.get_user_by_token(auth_token)

        remover_as_member = cls.check_user_in_group(remover.id, group_id, repository)

        cls.check_permissions(remover_as_member, "change_members")

        if member_id == remover.id:
            raise HaraKiriForbiddenError(
                "Remover cannot delete himself from the group. Use leave_group method instead."
            )

        repository.delete(UserGroup, member_id, group_id)
        repository.commit()

        return GroupService.get_group_members(group_id)

    @classmethod
    @use_repository
    def leave_group(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[UserGroupModel]:
        """
        Leave group.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            list[UserGroupModel] - List of user groups

        Raises:
            NotAuthorizedError: User not authorized
            UserNotInGroupError: User is not in the group
            HaraKiriForbiddenError: User is the owner of the group
        """
        user = UserService.get_user_by_token(auth_token)

        user_group = cls.check_user_in_group(user.id, group_id, repository)

        if user_group.owner:
            raise HaraKiriForbiddenError("User is the owner of the group")

        repository.delete(UserGroup, user.id, group_id)
        repository.commit()

        return UserService.get_user_groups(user.id, auth_token)

    @staticmethod
    def check_permissions(
        user_group: UserGroup,
        required_permission: str,
    ) -> None:
        """
        Check if user has required permission.
        """
        if not (user_group.owner or getattr(user_group, required_permission)):
            raise UserHasNoPermissionsError(
                f"User lacks {required_permission} permission"
            )

    @staticmethod
    def check_user_in_group(
        user_id: int,
        group_id: int,
        repository: Session,
        message: str = "User is not in the group",
    ) -> UserGroup:
        """
        Check if user is in the group.
        """
        user_group = repository.get(UserGroup, user_id, group_id)
        if not user_group:
            raise UserNotInGroupError(message)
        return user_group

    @staticmethod
    def _get_add_permission(
        permission: bool | None,
        adder_permission: bool,
        is_owner: bool,
    ) -> bool:
        """
        Get add permission.
        """
        if permission is None:
            return False
        return permission if is_owner else adder_permission and permission

    @staticmethod
    def _get_update_permission(
        permission: bool | None,
        updater_permission: bool,
        old_permission: bool,
        is_owner: bool,
    ) -> bool:
        """
        Get update permission.
        """
        if permission is None:
            return old_permission
        return permission if is_owner else updater_permission and permission

    @staticmethod
    def _transfer_ownership_if_needed(
        current_owner: UserGroup,
        new_owner_id: int,
        group_id: int,
        repository: Session,
    ) -> None:
        """
        Transfer ownership if needed.
        """
        if current_owner.owner:
            current_owner.owner = False
            group = repository.get(Group, group_id)
            group.owner_id = new_owner_id

    @classmethod
    def _calculate_add_permissions(
        cls,
        permissions: GroupPermissionsModel,
        adder: UserGroup,
    ) -> dict[str, bool]:
        """
        Calculate permissions.
        """
        return {
            permission: cls._get_add_permission(
                getattr(permissions, permission),
                adder.owner,
                adder.owner,
            )
            for permission in permissions.model_fields.keys()
        }

    @classmethod
    def _apply_update_permissions(
        cls,
        permissions: GroupPermissionsModel,
        updating: UserGroup,
        updater: UserGroup,
    ) -> None:
        """
        Apply update permissions.
        """
        for permission in permissions.model_fields.keys():
            updating.__setattr__(
                permission,
                cls._get_update_permission(
                    permission=getattr(permissions, permission),
                    updater_permission=getattr(updater, permission),
                    old_permission=getattr(updating, permission),
                    is_owner=updater.owner,
                ),
            )

    @classmethod
    @use_repository
    def check_user_in_group(
        cls,
        user_id: int,
        group_id: int,
        repository: Session,
    ) -> bool:
        """
        Check if user is in the group.
        """
        user_group = repository.get(UserGroup, (user_id, group_id))
        return user_group is not None
