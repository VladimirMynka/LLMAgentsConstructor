from sqlalchemy.orm import Session

from src.db.entities.agent import Agent, AgentType
from src.db.entities.ai_agent import AIAgent
from src.db.entities.prompt import Prompt
from src.db.entities.settings import Settings
from src.db.errors.agent import AgentNotFoundError
from src.db.errors.settings import SettingsNotFoundError
from src.db.services.agents.interfaces import ISpecificAgentService
from src.db.services.graph_service import GraphService
from src.db.services.prompt_service import PromptService
from src.db.services.settings_service import SettingsService
from src.models.agent import CreateUpdateAgentModel
from src.models.agent_details import AIDetails


class AIAgentService(ISpecificAgentService):
    """Service for AI agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> AIAgent:
        """
        Create AI agent entity. Additional method for creating AI agent.

        Args:
            data: CreateUpdateAgentModel - Agent data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session

        Returns:
            AIAgent: AIAgent model

        Raises:
            PromptNotFoundError: If prompt not found
            SettingsNotFoundError: If settings not found
        """
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
            prompt=prompt,
            settings=settings,
        )

        return entity

    @classmethod
    def get_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> AIDetails:
        """
        Get AI agent details.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            repository: Session - Database session

        Returns:
            AIDetails: AIDetails model

        Raises:
            AgentNotFoundError: If agent not found
        """
        ai_agent = repository.get_one(AIAgent, AIAgent.id == agent.id)
        prompt = PromptService.get_prompt_model(ai_agent.prompt)
        settings = SettingsService.get_settings_model(ai_agent.settings, user_id)

        return AIDetails(prompt=prompt, settings=settings)

    @classmethod
    def update_agent(
        cls,
        agent: Agent,
        user_id: int,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> AIAgent:
        """
        Update AI agent.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            data: CreateUpdateAgentModel - Agent data
            repository: Session - Database session

        Returns:
            AIAgent: AIAgent entity

        Raises:
            AgentNotFoundError: If agent not found
            PromptNotFoundError: If prompt not found
            SettingsNotFoundError: If settings not found
        """
        ai_agent = repository.get_one(AIAgent, AIAgent.id == agent.id)
        if not ai_agent:
            raise AgentNotFoundError("AI agent not found")

        details = data.details
        prompt = cls._get_prompt_from_request(details, user_id, repository)
        settings = cls._get_settings_from_request(details, user_id, repository)

        ai_agent.name = data.name
        ai_agent.description = data.description
        ai_agent.start_log_message = data.start_log_message
        ai_agent.finish_log_message = data.finish_log_message
        ai_agent.prompt = prompt
        ai_agent.settings = settings

        return ai_agent

    @classmethod
    def delete_agent(
        cls,
        agent_id: int,
        repository: Session,
    ) -> None:
        """
        Delete AI agent.

        Args:
            agent_id: int - Agent id
            graph_id: int - Graph id
            auth_token: str - Auth token
            repository: Session - Database session

        Raises:
            AgentNotFoundError: If AI agent not found
        """
        ai_agent = repository.get_one(AIAgent, AIAgent.id == agent_id)
        if not ai_agent:
            raise AgentNotFoundError("AI agent not found")

        repository.delete(ai_agent)

    @classmethod
    def get_agent_by_id(
        cls,
        agent_id: int,
        user_id: int,
        graph_id: int,
        repository: Session,
    ) -> AIAgent:
        """
        Get agent by id.

        Args:
            agent_id: int - Agent id
            user_id: int - User id
            graph_id: int - Graph id
            repository: Session - Database session

        Returns:
            AIAgent: AIAgent model

        Raises:
            AgentNotFoundError: If agent not found
        """
        agent = repository.get_one(AIAgent, AIAgent.id == agent_id)
        if (agent is None) or (agent.node.graph_id != graph_id):
            raise AgentNotFoundError("Agent not found")

        GraphService.check_user_has_access_to_graph(user_id, graph_id, repository)

        return agent

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
