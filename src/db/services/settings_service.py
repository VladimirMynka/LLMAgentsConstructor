from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.graph import Graph
from src.db.entities.group import Group
from src.db.entities.model import Model
from src.db.entities.provider import Provider
from src.db.entities.settings import Settings
from src.db.errors.graph import GraphNotFoundError
from src.db.errors.settings import SettingsNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.graph_service import GraphService
from src.db.services.model_service import ModelService
from src.db.services.provider_service import ProviderService
from src.db.services.user_service import UserService
from src.models.settings import CreateSettingsModel, SettingsModel


class SettingsService:
    """
    Group of methods for managing settings.
    """

    @classmethod
    @use_repository
    def get_settings(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[SettingsModel]:
        """
        Get all available settings in current context.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            list[SettingsModel] - List of settings

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        user_providers = cls._get_user_providers(user_model.id, repository)
        graph = cls._get_graph_with_access_check(graph_id, user_model.id, repository)
        graph_providers = cls._get_graph_providers(graph.id, repository)
        available_providers = user_providers.intersection(graph_providers)
        available_models = cls._get_available_models(available_providers)
        settings = cls._get_settings_for_models(available_models, repository)

        return [
            cls._create_settings_model(setting, user_model.id) for setting in settings
        ]

    @staticmethod
    def _get_user_providers(user_id: int, repository: Session) -> set[Provider]:
        """
        Get user providers.
        """
        user_groups = (
            repository.query(Group).filter(Group.members.any(user_id=user_id)).all()
        )
        return set(provider for group in user_groups for provider in group.providers)

    @staticmethod
    def _get_graph_with_access_check(
        graph_id: int,
        user_id: int,
        repository: Session,
    ) -> Graph:
        """
        Get graph with access check.
        """
        graph = repository.get(Graph, graph_id)
        GraphService.check_user_has_access_to_graph(user_id, graph_id, repository)
        if not graph:
            raise GraphNotFoundError("Graph not found")
        return graph

    @staticmethod
    def _get_graph_providers(graph_id: int, repository: Session) -> set[Provider]:
        """
        Get graph providers.
        """
        graph_groups = (
            repository.query(Group).filter(Group.graphs.any(graph_id=graph_id)).all()
        )
        return set(provider for group in graph_groups for provider in group.providers)

    @staticmethod
    def _get_available_models(providers: set[Provider]) -> set[Model]:
        """
        Get available models.
        """
        return set(model for provider in providers for model in provider.models)

    @staticmethod
    def _get_settings_for_models(
        models: set[Model],
        repository: Session,
    ) -> set[Settings]:
        """
        Get settings for models.
        """
        settings_list = [
            repository.query(Settings).filter(Settings.model_id == model.id).all()
            for model in models
        ]
        return set(setting for sublist in settings_list for setting in sublist)

    @staticmethod
    def _create_settings_model(setting: Settings, user_id: int) -> SettingsModel:
        """
        Create settings model.
        """
        return SettingsModel(
            id=setting.id,
            model=ModelService.get_expand_model(setting.model, user_id),
            temperature=setting.temperature,
            n=setting.n,
            frequency_penalty=setting.frequency_penalty,
            presence_penalty=setting.presence_penalty,
        )

    @classmethod
    def create_settings_without_commit(
        cls,
        data: CreateSettingsModel,
    ) -> Settings:
        """
        Create settings without committing to the database.
        Use for another services. Make all constraints checks by yourself.
        """
        return Settings(
            model_id=data.model_id,
            temperature=data.temperature,
            n=data.n,
            frequency_penalty=data.frequency_penalty,
            presence_penalty=data.presence_penalty,
        )

    @staticmethod
    def get_settings_model(setting: Settings, user_id: int) -> SettingsModel:
        """
        Get settings model.
        """
        return SettingsModel(
            id=setting.id,
            model=ModelService.get_expand_model(setting.model, user_id),
            temperature=setting.temperature,
            n=setting.n,
            frequency_penalty=setting.frequency_penalty,
            presence_penalty=setting.presence_penalty,
        )

    @classmethod
    @use_repository
    def check_user_has_access_to_settings(
        cls,
        user_id: int,
        settings_id: int,
        repository: Session,
    ) -> Settings:
        """Check if the user has access to the settings."""
        settings = repository.get_one(Settings, Settings.id == settings_id)
        if settings is None:
            raise SettingsNotFoundError("Settings not found")

        ProviderService.check_user_has_access_to_provider(
            user_id,
            settings.model.provider_id,
            repository,
        )

        return settings
