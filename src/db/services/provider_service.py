from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.group import Group
from src.db.entities.provider import Provider
from src.db.entities.provider_group import ProviderGroup
from src.db.entities.user import User
from src.db.entities.user_group import UserGroup
from src.db.errors.provider import ProviderNotFoundError, UserIsNotProviderOwnerError
from src.db.errors.user import UserNotFoundError
from src.db.services.user_service import UserService
from src.models.group import GroupModel
from src.models.provider import (
    CreateProviderRequestModel,
    ExpandProviderModel,
    ProviderModel,
    UpdateProviderRequestModel,
)


class ProviderService:
    """
    Group of methods for managing providers.
    """

    @classmethod
    @use_repository
    def get_providers(
        cls,
        auth_token: str,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Get all providers available for current user.

        Args:
            auth_token: str - Authentication token

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        providers: list[Provider] = cls._get_all_providers_of_user(
            user_model.id, repository
        )

        return [
            ProviderModel(
                id=provider.id,
                name=provider.name,
                url=provider.url,
            )
            for provider in providers
        ]

    @classmethod
    @use_repository
    def get_provider_by_id(
        cls,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandProviderModel:
        """
        Get provider by id.

        Args:
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            ExpandProviderModel - Provider

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token)

        cls.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get(Provider, provider_id)
        if not provider:
            raise ProviderNotFoundError("Provider not found")

        return ExpandProviderModel(
            id=provider.id,
            name=provider.name,
            url=provider.url,
            groups=[
                GroupModel(
                    id=provider_group.group_id,
                    name=provider_group.group.name,
                )
                for provider_group in provider.groups
            ],
        )

    @classmethod
    @use_repository
    def create_provider(
        cls,
        provider_model: CreateProviderRequestModel,
        auth_token: str,
        repository: Session,
    ) -> ProviderModel:
        """
        Create a new provider.

        Args:
            provider_model: CreateProviderRequestModel - Provider model
            auth_token: str - Authentication token

        Returns:
            ProviderModel - Created provider

        Raises:
            NotAuthorizedError: If the authentication token is invalid
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        provider = Provider(
            name=provider_model.name,
            url=provider_model.url,
        )
        repository.add(provider)

        provider_group = ProviderGroup(
            provider=provider,
            group=base_group,
        )
        repository.add(provider_group)

        repository.commit()
        repository.refresh(provider)

        return ProviderModel(
            id=provider.id,
            name=provider.name,
            url=provider.url,
        )

    @classmethod
    @use_repository
    def update_provider(
        cls,
        provider_id: int,
        provider_model: UpdateProviderRequestModel,
        auth_token: str,
        repository: Session,
    ) -> Provider:
        """
        Update provider by id.

        Args:
            provider_id: int - Provider id
            provider_model: UpdateProviderRequestModel - Provider model
            auth_token: str - Authentication token

        Returns:
            Provider - Updated provider

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            UserIsNotProviderOwnerError: If the user is not owner of the provider
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get_one(Provider, provider_id)
        if not provider:
            raise ProviderNotFoundError("Provider not found")

        provider_group = repository.get_one(
            ProviderGroup,
            ProviderGroup.provider_id == provider_id,
            ProviderGroup.group_id == base_group.id,
        )
        if not provider_group:
            raise UserIsNotProviderOwnerError("User is not owner of this provider")

        provider.name = provider_model.name
        provider.url = provider_model.url

        repository.commit()

        return provider

    @classmethod
    @use_repository
    def delete_provider(
        cls,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Delete provider by id.

        Args:
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            UserIsNotProviderOwnerError: If the user is not owner of the provider
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user: User = repository.get_one(User, User.id == user_model.id)
        base_group: Group = user.base_group

        cls.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get_one(Provider, provider_id)
        if not provider:
            raise ProviderNotFoundError("Provider not found")

        provider_group = repository.get_one(
            ProviderGroup,
            ProviderGroup.provider_id == provider_id,
            ProviderGroup.group_id == base_group.id,
        )
        if not provider_group:
            raise UserIsNotProviderOwnerError("User is not owner of this provider")

        repository.delete(provider)
        repository.commit()

        return cls.get_providers(auth_token, repository)

    @classmethod
    @use_repository
    def _get_all_providers_of_user(
        cls,
        user_id: int,
        repository: Session,
    ) -> list[Provider]:
        """
        Get all providers available for current user.
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        providers: list[Provider] = sum([group.providers for group in groups], [])

        return providers

    @classmethod
    @use_repository
    def check_user_has_access_to_provider(
        cls,
        user_id: int,
        provider_id: int,
        repository: Session,
    ):
        """
        Check if the user has access to the provider.

        Args:
            user_id: int - User id
            provider_id: int - Provider id

        Raises:
            UserNotFoundError: If the user is not found
            ProviderNotFoundError: If the provider is not found or user has no access to it
        """
        user = repository.get_one(User, User.id == user_id)
        if not user:
            raise UserNotFoundError("User not found")

        provider = repository.get_one(Provider, Provider.id == provider_id)
        if not provider:
            raise ProviderNotFoundError("Provider not found")

        user_groups: list[UserGroup] = (
            repository.query(UserGroup).filter(UserGroup.user_id == user_id).all()
        )
        groups: list[Group] = [user_group.group for user_group in user_groups]

        if provider not in sum([group.providers for group in groups], []):
            raise ProviderNotFoundError("User has no access to this provider")
