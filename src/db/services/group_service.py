from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities import Group
from src.db.entities.user_group import UserGroup
from src.db.errors.group import (
    GroupAlreadyExistsError,
    GroupNotFoundError,
    HaraKiriForbiddenError,
    UserAlreadyInGroupError,
    UserNotInGroupError,
)
from src.db.errors.user import UserHasNoPermissionsError, UserNotFoundError
from src.db.services.user_service import UserService
from src.models.graph import GraphModel
from src.models.group import (
    AddMemberRequestModel,
    CreateGroupRequestModel,
    DeleteGroupResponseModel,
    ExpandGroupModel,
    GetGroupByIdRequestModel,
    GroupModel,
    GroupPermissionsModel,
    MemberModel,
    UpdateGroupRequestModel,
)
from src.models.user import UserModel


class GroupService:
    @use_repository
    def get_group_by_id(
        cls,
        data: GetGroupByIdRequestModel,
        auth_token: str,
        repository: Session,
    ) -> ExpandGroupModel:
        """
        Get group by id.

        Args:
            data: GetGroupByIdRequestModel - Get group by id request model
            auth_token: str - Auth token

        Returns:
            ExpandGroupModel - Expand group model

        Raises:
            NotAuthorizedError - User not authorized
            GroupNotFoundError - Group not found
            UserNotInGroupError - User is not in the group
        """
        user: UserModel = UserService.get_user_by_auth_token(auth_token, repository)
        
        user_group = repository.get(UserGroup, user.id, data.id)
        if not user_group:
            raise UserNotInGroupError("User is not in the group")

        group = repository.get(Group, data.id)
        if not group:
            raise GroupNotFoundError
        return GroupModel(
            id=group.id,
            name=group.name,
            owner=UserModel.model_validate(group.owner, from_attributes=True),
            members=list(
                map(
                    lambda user: MemberModel.model_validate(user, from_attributes=True),
                    group.members,
                )
            ),
            graphs=list(
                map(
                    lambda graph: GraphModel.model_validate(
                        graph, from_attributes=True
                    ),
                    group.graphs,
                )
            ),
        )

    def get_group_owner(
        cls,
        data: GetGroupByIdRequestModel,
        auth_token: str,
        repository: Session,
    ) -> UserModel:
        """
        Get group owner.

        Args:
            data: GetGroupByIdRequestModel - Get group by id request model
            auth_token: str - Auth token

        Returns:
            UserModel - User model

        Raises:
            NotAuthorizedError - User not authorized
            GroupNotFoundError - Group not found
            UserNotInGroupError - User is not in the group
        """
        group = cls.get_group_by_id(data, auth_token, repository)
        return group.owner

    def get_group_members(cls, data: GetGroupByIdRequestModel) -> list[MemberModel]:
        """
        Get group members.

        Args:
            data: GetGroupByIdRequestModel - Get group by id request model

        Returns:
            list[MemberModel] - List of group members

        Raises:
            GroupNotFoundError - Group not found
        """
        group = cls.get_group_by_id(data)
        return group.members

    def get_group_graphs(cls, data: GetGroupByIdRequestModel) -> list[GraphModel]:
        """
        Get group graphs.

        Args:
            data: GetGroupByIdRequestModel - Get group by id request model

        Returns:
            list[GraphModel] - List of group graphs

        Raises:
            GroupNotFoundError - Group not found
        """
        group = cls.get_group_by_id(data)
        return group.graphs

    @use_repository
    def create_group(
        cls,
        data: CreateGroupRequestModel,
        auth_token: str,
        repository: Session,
    ) -> ExpandGroupModel:
        """
        Create group.

        Args:
            data: CreateGroupRequestModel - Create group request model
            auth_token: str - Auth token

        Returns:
            ExpandGroupModel - Expand group model

        Raises:
            NotAuthorizedError - User not authorized
        """
        owner = UserService.get_user_by_token(auth_token)
        
        group = Group(name=data.name, owner_id=owner.id)
        repository.add(group)

        if owner.id not in data.members:
            data.members.append(owner.id)

        for member_id in data.members:
            permission = member_id == owner.id
            user_group = UserGroup(
                user_id=member_id,
                group_id=group.id,
                owner=permission,
                change_members=permission,
                add_graphs=permission,
                run_graphs=permission,
                change_graphs_permissions=permission,
                delete_graphs=permission,
            )
            repository.add(user_group)

        repository.commit()
        return cls.get_group_by_id(GetGroupByIdRequestModel(id=group.id))

    @use_repository
    def add_group_member(
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
            NotAuthorizedError - User not authorized
            UserHasNoPermissionsError - User has no permissions
        """
        adder = UserService.get_user_by_token(auth_token)

        adder_as_member = repository.get(UserGroup, adder.id, group_id)

        if not adder_as_member:
            raise UserNotInGroupError("Adder is not in the group")

        if (not adder_as_member.owner) and (not adder_as_member.change_members):
            raise UserHasNoPermissionsError(
                "Adder has no permissions to add users to the group"
            )

        def get_permission(permission: bool | None, adder_permission: bool) -> bool:
            """
            Get permission taking into account adder's permissions.
            """
            if permission is None:
                return False
            if adder_as_member.owner:
                return permission
            return adder_permission and permission

        maybe_existing_user_group = repository.get(UserGroup, data.user_id, group_id)
        if maybe_existing_user_group:
            raise UserAlreadyInGroupError("User is already in the group.")

        if adder_as_member.owner and data.permissions.owner:
            adder_as_member.owner = False
            group = repository.get(Group, group_id)
            group.owner_id = data.user_id

        new_user_group = UserGroup(
            user_id=data.user_id,
            group_id=group_id,
            owner=get_permission(data.permissions.owner, adder_as_member.owner),
            change_members=get_permission(
                data.permissions.change_members, adder_as_member.change_members
            ),
            add_graphs=get_permission(
                data.permissions.add_graphs, adder_as_member.add_graphs
            ),
            run_graphs=get_permission(
                data.permissions.run_graphs, adder_as_member.run_graphs
            ),
            change_graphs_permissions=get_permission(
                data.permissions.change_graphs_permissions,
                adder_as_member.change_graphs_permissions,
            ),
            delete_graphs=get_permission(
                data.permissions.delete_graphs, adder_as_member.delete_graphs
            ),
        )

        repository.add(new_user_group)
        repository.commit()

        return cls.get_group_members(GetGroupByIdRequestModel(id=group_id))

    @use_repository
    def update_group_member(
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
            NotAuthorizedError - User not authorized
            UserNotInGroupError - User is not in the group
            UserHasNoPermissionsError - User has no permissions to edit users permissions
        """
        adder = UserService.get_user_by_token(auth_token)

        adder_as_member = repository.get(UserGroup, adder.id, group_id)

        if not adder_as_member:
            raise UserNotInGroupError("Adder is not in the group")

        if (not adder_as_member.owner) and (not adder_as_member.change_members):
            raise UserHasNoPermissionsError(
                "Adder has no permissions to edit users permissions"
            )

        def get_permission(
            permission: bool | None,
            adder_permission: bool,
            old_permission: bool,
        ) -> bool:
            """
            Get permission taking into account adder's permissions.
            """
            if permission is None:
                return old_permission
            if adder_as_member.owner:
                return permission
            return adder_permission and permission

        if adder_as_member.owner and data.owner:
            adder_as_member.owner = False
            group = repository.get(Group, group_id)
            group.owner_id = member_id

        updating_member = repository.get(UserGroup, member_id, group_id)

        if not updating_member:
            raise UserNotFoundError("User is not in the group")

        updating_member.owner = get_permission(
            data.owner, adder_as_member.owner, updating_member.owner
        )
        updating_member.change_members = get_permission(
            data.change_members,
            adder_as_member.change_members,
            updating_member.change_members,
        )
        updating_member.add_graphs = get_permission(
            data.add_graphs, adder_as_member.add_graphs, updating_member.add_graphs
        )
        updating_member.run_graphs = get_permission(
            data.run_graphs, adder_as_member.run_graphs, updating_member.run_graphs
        )
        updating_member.change_graphs_permissions = get_permission(
            data.change_graphs_permissions,
            adder_as_member.change_graphs_permissions,
            updating_member.change_graphs_permissions,
        )
        updating_member.delete_graphs = get_permission(
            data.delete_graphs,
            adder_as_member.delete_graphs,
            updating_member.delete_graphs,
        )

        repository.commit()

        return cls.get_group_members(GetGroupByIdRequestModel(id=group_id))

    @use_repository
    def delete_group_member(
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
            NotAuthorizedError - User not authorized
            UserNotInGroupError - User is not in the group
            UserHasNoPermissionsError - User has no permissions to delete users from the group
            HaraKiriForbiddenError - User is the owner of the group
        """
        remover = UserService.get_user_by_token(auth_token)

        remover_as_member = repository.get(UserGroup, remover.id, group_id)

        if not remover_as_member:
            raise UserNotInGroupError("Remover is not in the group")

        if (not remover_as_member.owner) and (not remover_as_member.change_members):
            raise UserHasNoPermissionsError(
                "Remover has no permissions to delete users from the group"
            )

        if member_id == remover.id:
            raise HaraKiriForbiddenError("Remover cannot delete himself from the group")

        repository.delete(UserGroup, member_id, group_id)
        repository.commit()

        return cls.get_group_members(GetGroupByIdRequestModel(id=group_id))

    @use_repository
    def leave_group(
        cls, group_id: int, auth_token: str, repository: Session
    ) -> list[MemberModel]:
        """
        Leave group.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            list[MemberModel] - List of group members

        Raises:
            NotAuthorizedError - User not authorized
            UserNotInGroupError - User is not in the group
            HaraKiriForbiddenError - User is the owner of the group
        """
        user = UserService.get_user_by_token(auth_token)

        user_group = repository.get(UserGroup, user.id, group_id)

        if not user_group:
            raise UserNotInGroupError("User is not in the group")

        if user_group.owner:
            raise HaraKiriForbiddenError("User is the owner of the group")

        repository.delete(UserGroup, user.id, group_id)
        repository.commit()

        return cls.get_group_members(GetGroupByIdRequestModel(id=group_id))

    @use_repository
    def update_group(
        cls,
        data: UpdateGroupRequestModel,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandGroupModel:
        """
        Update group.

        Args:
            data: UpdateGroupRequestModel - Update group request model
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            ExpandGroupModel - Expand group model

        Raises:
            NotAuthorizedError - User not authorized
            GroupNotFoundError - Group not found
            UserHasNoPermissionsError - User is not the owner of the group
        """
        updater = UserService.get_user_by_token(auth_token)

        group = repository.get(Group, group_id)

        if not group:
            raise GroupNotFoundError("Group not found")

        if updater.id != group.owner_id:
            raise UserHasNoPermissionsError("User is not the owner of the group")

        if data.name:
            group.name = data.name

        repository.commit()
        return cls.get_group_by_id(GetGroupByIdRequestModel(id=group_id))

    @use_repository
    def delete_group(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> DeleteGroupResponseModel:
        """
        Delete group.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            DeleteGroupResponseModel - Delete group response model

        Raises:
            GroupNotFoundError - Group not found
            UserHasNoPermissionsError - User is not the owner of the group
            NotAuthorizedError - User not authorized
        """
        deleter = UserService.get_user_by_token(auth_token)

        group = repository.get(Group, group_id)

        if not group:
            raise GroupNotFoundError("Group not found")

        if deleter.id != group.owner_id:
            raise UserHasNoPermissionsError("User is not the owner of the group")

        repository.delete(Group, group_id)
        repository.commit()

        return DeleteGroupResponseModel(id=group_id)
