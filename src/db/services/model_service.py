from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.model import Model
from src.db.entities.provider import Provider
from src.db.errors.model import ModelAlreadyExistsError, ModelNotFoundError
from src.db.services.provider_service import ProviderService
from src.db.services.provider_token_service import ProviderTokenService
from src.db.services.user_service import UserService
from src.models.model import (
    CreateModelRequestModel,
    ExpandModelModel,
    ModelModel,
    UpdateModelRequestModel,
)
from src.models.provider import ProviderModel


class ModelService:
    """
    Group of methods for managing models.
    """

    @classmethod
    @use_repository
    def get_models(
        cls,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ModelModel]:
        """
        Get all models of current provider.

        Args:
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            list[ModelModel] - List of models

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        ProviderService.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get_one(Provider, Provider.id == provider_id)
        models = provider.models

        return [
            ModelModel(
                id=model.id,
                name=model.name,
                owner=model.owner,
            )
            for model in models
        ]

    @classmethod
    @use_repository
    def get_model_by_id(
        cls,
        model_id: int,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExpandModelModel:
        """
        Get model by id.

        Args:
            model_id: int - Model id
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            ExpandModelModel - Model

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            ModelNotFoundError: If the model is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token)
        ProviderService.check_user_has_access_to_provider(user_model.id, provider_id)

        model = repository.get_one(Model, Model.id == model_id)
        if not model:
            raise ModelNotFoundError("Model not found")

        if model.provider_id != provider_id:
            raise ModelNotFoundError("Model not found")

        return ExpandModelModel(
            id=model.id,
            name=model.name,
            owner=model.owner,
            provider=ProviderModel(
                id=model.provider.id,
                name=model.provider.name,
                url=model.provider.url,
                has_token=ProviderTokenService.has_token(
                    user_model.id,
                    model.provider_id,
                ),
            ),
        )

    @classmethod
    @use_repository
    def create_model(
        cls,
        provider_id: int,
        model_model: CreateModelRequestModel,
        auth_token: str,
        repository: Session,
    ) -> list[ModelModel]:
        """
        Create a new model.

        Args:
            provider_id: int - Provider id
            model_model: CreateModelRequestModel - Model model
            auth_token: str - Authentication token

        Returns:
            list[ModelModel] - List of models

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            ModelAlreadyExistsError: If the model already exists
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        ProviderService.check_user_has_access_to_provider(user_model.id, provider_id)

        provider = repository.get_one(Provider, Provider.id == provider_id)

        maybe_existing_model = repository.get_one(
            Model,
            Model.name == model_model.name,
            Model.owner == model_model.owner,
            Model.provider_id == provider_id,
        )
        if maybe_existing_model is not None:
            raise ModelAlreadyExistsError("Model already exists")

        model = Model(
            name=model_model.name,
            owner=model_model.owner,
            provider_id=provider.id,
        )
        repository.add(model)

        repository.commit()

        return cls.get_models(provider_id, auth_token)

    @classmethod
    @use_repository
    def update_model(
        cls,
        model_id: int,
        provider_id: int,
        data: UpdateModelRequestModel,
        auth_token: str,
        repository: Session,
    ) -> list[ModelModel]:
        """
        Update model by id.

        Args:
            model_id: int - Model id
            provider_id: int - Provider id
            data: UpdateModelRequestModel - Data to update
            auth_token: str - Authentication token

        Returns:
            list[ModelModel] - List of models

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            ModelNotFoundError: If the model is not found
            ModelAlreadyExistsError: If the model already exists
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        ProviderService.check_user_has_access_to_provider(user_model.id, provider_id)

        model = repository.get_one(Model, Model.id == model_id)
        if not model:
            raise ModelNotFoundError("Model not found")

        if model.provider_id != provider_id:
            raise ModelNotFoundError("Model not found")

        maybe_existing_model = repository.get_one(
            Model,
            Model.name == data.name,
            Model.owner == data.owner,
            Model.provider_id == provider_id,
        )
        if maybe_existing_model is not None:
            raise ModelAlreadyExistsError("Model already exists")

        model.name = data.name
        model.owner = data.owner

        repository.commit()

        return cls.get_models(provider_id, auth_token)

    @classmethod
    @use_repository
    def delete_model(
        cls,
        model_id: int,
        provider_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ModelModel]:
        """
        Delete model by id.

        Args:
            model_id: int - Model id
            provider_id: int - Provider id
            auth_token: str - Authentication token

        Returns:
            list[ModelModel] - List of models

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            ProviderNotFoundError: If the provider is not found or user has no access to it
            ModelNotFoundError: If the model is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        cls._check_user_has_access_to_provider(user_model.id, provider_id)

        model = repository.get_one(Model, Model.id == model_id)
        if not model:
            raise ModelNotFoundError("Model not found")

        if model.provider_id != provider_id:
            raise ModelNotFoundError("Model not found")

        repository.delete(model)
        repository.commit()

        return cls.get_models(provider_id, auth_token)

    def get_expand_model(model: Model, user_id: int) -> ExpandModelModel:
        """
        Get expand model.

        Args:
            model: Model - Model
            user_id: int - User id

        Returns:
            ExpandModelModel - Expand model
        """
        return ExpandModelModel(
            id=model.id,
            name=model.name,
            owner=model.owner,
            provider=ProviderModel(
                id=model.provider_id,
                name=model.provider.name,
                url=model.provider.url,
                has_token=ProviderTokenService.has_token(
                    user_id,
                    model.provider_id,
                ),
            ),
        )
