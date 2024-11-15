from sqlalchemy.orm import Session

from src.db.entities.agent import AgentType
from src.db.entities.ai_agent import AIAgent
from src.db.entities.prompt import Prompt
from src.db.entities.settings import Settings
from src.db.errors.settings import SettingsNotFoundError
from src.db.services.prompt_service import PromptService
from src.db.services.settings_service import SettingsService
from src.models.agent import CreateUpdateAgentModel


class AIAgentService:
    """Service for AI agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> AIAgent:
        """Create AI agent entity. Additional method for creating AI agent."""
        details = data.details

        prompt = cls._get_prompt_from_request(details, user_id, repository)
        settings = cls._get_settings_from_request(details, user_id, repository)

        entity = AIAgent(
            agent_type=AgentType.ai,
            name=data.name,
            description=data.description,
            start_log_message=data.start_log_message,
            finish_log_message=data.finish_log_message,
            node_id=node_id,
            prompt_id=prompt.id,
            settings_id=settings.id,
        )

        return entity

    @classmethod
    def _get_prompt_from_request(
        cls,
        details: CreateUpdateAgentModel,
        user_id: int,
        repository: Session,
    ) -> Prompt:
        """
        Get prompt from request.

        Args:
            details: CreateUpdateAgentModel - Details from request
            user_id: int - User id
            repository: Session - Database session

        Returns:
            Prompt: Prompt model

        Raises:
            UserNotFoundError: If user not found
            PromptNotFoundError: If prompt not found
        """
        prompt = PromptService.check_user_has_access_to_prompt(
            user_id, details.prompt_id, repository
        )

        return prompt

    @classmethod
    def _get_settings_from_request(
        cls,
        details: CreateUpdateAgentModel,
        user_id: int,
        repository: Session,
    ) -> Settings:
        """
        Get settings from request.

        Args:
            details: CreateUpdateAgentModel - Details from request
            user_id: int - User id
            repository: Session - Database session

        Returns:
            Settings: Settings model

        Raises:
            SettingsNotFoundError: If settings not found
        """
        if details.settings is not None:
            return SettingsService.create_settings_without_commit(details.settings)

        elif details.settings_id is not None:
            return SettingsService.check_user_has_access_to_settings(
                user_id, details.settings_id, repository
            )

        raise SettingsNotFoundError("Settings not found")
