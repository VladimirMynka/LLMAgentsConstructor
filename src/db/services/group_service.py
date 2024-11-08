from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities import Group
from src.db.entities.user_group import UserGroup
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.user import UserHasNoPermissionsError
from src.db.services.user_service import UserService
from src.models.graph import GraphModel
from src.models.group import (
    CreateGroupRequestModel,
    DeleteGroupResponseModel,
    ExpandGroupModel,
    GroupModel,
    MemberModel,
    UpdateGroupRequestModel,
)
from src.models.user import UserModel


class GroupService:
    @use_repository
    def get_group_by_id(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandGroupModel:
        """
        Get group by id.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            ExpandGroupModel - Expand group model

        Raises:
            NotAuthorizedError: User not authorized
            GroupNotFoundError: Group not found
            UserNotInGroupError: User is not in the group
        """
        user: UserModel = UserService.get_user_by_auth_token(auth_token, repository)

        user_group = repository.get(UserGroup, user.id, group_id)
        if not user_group:
            raise UserNotInGroupError("User is not in the group")

        group = repository.get(Group, group_id)
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

    def get_owner(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> UserModel:
        """
        Get group owner.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            UserModel - User model

        Raises:
            NotAuthorizedError: User not authorized
            GroupNotFoundError: Group not found
            UserNotInGroupError: User is not in the group
        """
        group = cls.get_group_by_id(group_id, auth_token, repository)
        return group.owner

    def get_graphs(cls, group_id: int, auth_token: str) -> list[GraphModel]:
        """
        Get group graphs.

        Args:
            group_id: int - Group id
            auth_token: str - Auth token

        Returns:
            list[GraphModel] - List of group graphs

        Raises:
            NotAuthorizedError: User not authorized
            GroupNotFoundError: Group not found
            UserNotInGroupError: User is not in the group
        """
        group = cls.get_group_by_id(group_id, auth_token)
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
            NotAuthorizedError: User not authorized
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
        return cls.get_group_by_id(group.id)

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
            NotAuthorizedError: User not authorized
            GroupNotFoundError: Group not found
            UserHasNoPermissionsError: User is not the owner of the group
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
        return cls.get_group_by_id(group_id)

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
            GroupNotFoundError: Group not found
            UserHasNoPermissionsError: User is not the owner of the group
            NotAuthorizedError: User not authorized
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
