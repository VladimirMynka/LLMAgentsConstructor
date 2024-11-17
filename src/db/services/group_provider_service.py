from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.group import Group
from src.db.entities.provider import Provider
from src.db.entities.provider_group import ProviderGroup
from src.db.entities.provider_token import ProviderToken
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.provider import ProviderAlreadyInGroupError, ProviderNotFoundError
from src.db.services.member_service import MemberService
from src.db.services.user_service import UserService
from src.models.provider import AddProviderToGroupRequestModel, ProviderModel


class GroupProviderService:
    """
    Group of methods for managing group providers.
    """

    @classmethod
    @use_repository
    def get_group_providers(
        cls,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Get all providers available for current group.

        Args:
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GroupNotFoundError: If the group is not found
            UserNotInGroupError: If the user is not in the group
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        group = repository.get_one(Group, Group.id == group_id)
        if not group:
            raise GroupNotFoundError("Group not found")

        if not MemberService.check_user_in_group(user_model.id, group_id):
            raise UserNotInGroupError("User is not in the group")

        providers: list[Provider] = [relation.provider for relation in group.providers]

        return [
            ProviderModel(
                id=provider.id,
                name=provider.name,
                url=provider.url,
                has_token=bool(
                    repository.get_one(
                        ProviderToken,
                        ProviderToken.provider_id == provider.id,
                        ProviderToken.user_id == user_model.id,
                    )
                ),
            )
            for provider in providers
        ]

    @classmethod
    @use_repository
    def add_group_provider(
        cls,
        data: AddProviderToGroupRequestModel,
        group_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Add provider to group.

        Args:
            data: AddProviderToGroupRequestModel - Add provider to group request model
            group_id: int - Group id
            auth_token: str - Authentication token

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GroupNotFoundError: If the group is not found
            UserNotInGroupError: If the user is not in the group
            ProviderNotFoundError: If the provider is not found
            ProviderAlreadyInGroupError: If the provider is already in the group
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        group = repository.get_one(Group, Group.id == group_id)
        if not group:
            raise GroupNotFoundError("Group not found")

        if not MemberService.check_user_in_group(user_model.id, group_id):
            raise UserNotInGroupError("User is not in the group")

        provider = repository.get_one(Provider, Provider.id == data.provider_id)
        if not provider:
            raise ProviderNotFoundError("Provider not found")

        if repository.get_one(
            ProviderGroup,
            ProviderGroup.provider_id == provider.id,
            ProviderGroup.group_id == group_id,
        ):
            raise ProviderAlreadyInGroupError("Provider already in the group")

        repository.add(ProviderGroup(provider_id=provider.id, group_id=group_id))
        repository.commit()

        return cls.get_group_providers(group_id, auth_token, repository)
