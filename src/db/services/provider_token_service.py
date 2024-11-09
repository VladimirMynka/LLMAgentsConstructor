from openai import OpenAI
from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.provider import Provider
from src.db.entities.provider_token import ProviderToken
from src.db.errors.provider import ProviderTokenNotFoundError
from src.db.services.provider_service import ProviderService
from src.db.services.user_service import UserService
from src.models.provider import ProviderModel, TestConnectionResponseModel
from src.models.provider_token import CreateProviderTokenRequestModel


class ProviderTokenService:
    """
    Group of methods for managing provider tokens.
    """

    @classmethod
    @use_repository
    def add_provider_token(
        cls,
        data: CreateProviderTokenRequestModel,
        auth_token: str,
        provider_id: int,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Add or update provider token.

        Args:
            data: CreateProviderTokenRequestModel - Provider token data
            auth_token: str - Authentication token
            provider_id: int - Provider id

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the user is not authorized
            ProviderNotFoundError: If the provider is not found
        """

        user_model = UserService.get_user_by_auth_token(auth_token)
        ProviderService.check_user_has_access_to_provider(
            user_model.id, provider_id, repository
        )

        provider_token = repository.get_one(
            ProviderToken,
            ProviderToken.user_id == user_model.id,
            ProviderToken.provider_id == provider_id,
        )

        if provider_token is None:
            provider_token = ProviderToken(
                user_id=user_model.id,
                provider_id=provider_id,
                token=data.token,
            )
            repository.add(provider_token)
        else:
            provider_token.token = data.token
            repository.update(provider_token)

        repository.commit()

        return ProviderService.get_providers(user_model.id)

    @classmethod
    @use_repository
    def delete_provider_token(
        cls,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ProviderModel]:
        """
        Delete provider token.

        Args:
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            list[ProviderModel] - List of providers

        Raises:
            NotAuthorizedError: If the user is not authorized
            ProviderNotFoundError: If the provider is not found
        """

        user_model = UserService.get_user_by_auth_token(auth_token)
        ProviderService.check_user_has_access_to_provider(
            user_model.id, provider_id, repository
        )

        provider_token = repository.get_one(
            ProviderToken,
            ProviderToken.user_id == user_model.id,
            ProviderToken.provider_id == provider_id,
        )

        if provider_token is None:
            raise ProviderTokenNotFoundError

        repository.delete(provider_token)
        repository.commit()

        return ProviderService.get_providers(user_model.id)

    @classmethod
    @use_repository
    def test_connection(
        cls,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> TestConnectionResponseModel:
        """
        Test connection to provider.

        Args:
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            TestConnectionResponseModel - Test connection response

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        cls.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get_one(Provider, provider_id)

        token = repository.get_one(
            ProviderToken,
            ProviderToken.provider_id == provider_id,
            ProviderToken.user_id == user_model.id,
        )

        if not token:
            raise ProviderTokenNotFoundError("Provider token not found")

        try:
            openai = OpenAI(api_key=token.token, base_url=provider.url)
            available_models = openai.models.list()
        except Exception as e:
            return TestConnectionResponseModel(
                status=False,
                message=str(e),
            )

        return TestConnectionResponseModel(
            status=True,
            message="Connection to provider is successful. Available models: "
            + ", ".join([model.id for model in available_models]),
        )
