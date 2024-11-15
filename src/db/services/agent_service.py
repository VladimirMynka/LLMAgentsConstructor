from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.agent import Agent, AgentType
from src.db.entities.ai_agent import AIAgent
from src.db.entities.chat_agent import ChatAgent
from src.db.entities.critic_agent import CriticAgent
from src.db.entities.hard_code_agent import HardCodeAgent
from src.db.entities.node import Node
from src.db.entities.prompt import Prompt
from src.db.entities.settings import Settings
from src.db.errors.agent import AgentNotFoundError, CriticizedAgentNotFoundError
from src.db.services.graph_service import GraphService
from src.db.services.prompt_service import PromptService
from src.db.services.settings_service import SettingsService
from src.db.services.user_service import UserService
from src.models.agent import (
    AIDetails,
    ChatDetails,
    CreateUpdateAgentModel,
    CriticDetails,
    ExtendedAgentModel,
    HardCodeDetails,
)
from src.models.node import ContentType, NodeModel
from src.models.prompt import PromptModel
from src.models.settings import SettingsModel


class AgentService:
    """
    Group of methods for managing agents.
    """

    @classmethod
    @use_repository
    def get_agents(
        cls,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ExtendedAgentModel]:
        """
        Get all agents of the graph.

        Args:
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            list[ExtendedAgentModel] - List of agents

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)

        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        agents = (
            repository.query(Agent)
            .filter(
                Agent.node_id.in_(
                    repository.query(Node)
                    .filter(Node.graph_id == graph_id)
                    .with_only_columns(Node.id)
                    .subquery()
                )
            )
            .all()
        )

        return [
            cls._make_agent_model(agent, user_model.id, repository) for agent in agents
        ]

    @classmethod
    def get_agent(
        cls,
        agent_id: int,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> ExtendedAgentModel:
        """
        Get agent by id.

        Args:
            agent_id: int - Agent id
            graph_id: int - Graph id
            auth_token: str - Authentication token
            repository: Session - Database session

        Returns:
            ExtendedAgentModel - Agent

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            AgentNotFoundError: If the agent is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id, repository)

        agent = repository.get_one(Agent, Agent.id == agent_id)
        if (not agent) or (agent.node.graph_id != graph_id):
            raise AgentNotFoundError("Agent not found")

        return cls._make_agent_model(agent, user_model.id, repository)

    @classmethod
    @use_repository
    def create_agent(
        cls,
        graph_id: int,
        agent_type: str,
        auth_token: str,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> list[ExtendedAgentModel]:
        """
        Create agent.

        Args:
            graph_id: int - Graph id
            agent_type: str - Agent type
            auth_token: str - Authentication token
            data: CreateUpdateAgentModel - Data
            repository: Session - Database session

        Returns:
            ExtendedAgentModel - Agent

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
        """
        user_model = UserService.get_user_by_auth_token(auth_token)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        node = Node(
            graph_id=graph_id,
            x=data.node.x,
            y=data.node.y,
        )
        repository.add(node)

        agent = cls._create_specific_agent(data, node.id, agent_type)
        repository.add(agent)

        return cls.get_agent(agent.id, graph_id, auth_token, repository)

    @classmethod
    def _make_agent_model(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> ExtendedAgentModel:
        """
        Make agent model.
        """
        return ExtendedAgentModel(
            id=agent.id,
            name=agent.name,
            agent_type=agent.agent_type,
            description=agent.description,
            start_log_message=agent.start_log_message,
            finish_log_message=agent.finish_log_message,
            details=cls._get_agent_details(agent, user_id, repository),
            node=NodeModel(
                id=agent.node_id,
                x=agent.node.x,
                y=agent.node.y,
                content_type=ContentType.AGENT,
            ),
        )

    @classmethod
    def _get_agent_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> AIDetails | HardCodeDetails:
        """
        Get agent details.

        Args:
            agent: Agent - Agent
            user_id: int - User id
            repository: Session - Database session

        Returns:
            AIDetails | HardCodedDetails - Agent details

        Raises:
            ValidationError: If the agent type is invalid
        """
        if agent.agent_type in [
            AgentType.ai,
            AgentType.chat,
            AgentType.critic,
        ]:
            return cls._get_ai_agent_details(agent, user_id, repository)

        elif agent.agent_type in [
            AgentType.hard_code,
        ]:
            return cls._get_hard_code_agent_details(agent, repository)

        raise ValidationError("Invalid agent type")

    @classmethod
    def _get_ai_agent_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> AIDetails:
        """
        Get AI agent details.
        """
        ai_agent = repository.get_one(AIAgent, AIAgent.id == agent.id)
        prompt = PromptService.get_prompt_model(ai_agent.prompt)
        settings = SettingsService.get_settings_model(ai_agent.settings, user_id)

        if agent.agent_type == AgentType.chat:
            return cls._get_chat_agent_details(agent, prompt, settings, repository)

        elif agent.agent_type == AgentType.critic:
            return cls._get_critic_agent_details(agent, prompt, settings, repository)

        return AIDetails(prompt=prompt, settings=settings)

    @classmethod
    def _get_hard_code_agent_details(
        cls,
        agent: Agent,
        repository: Session,
    ) -> HardCodeDetails:
        """
        Get hard code agent details.
        """
        hard_coded_agent = repository.get_one(
            HardCodeAgent, HardCodeAgent.id == agent.id
        )
        return HardCodeDetails(predefined_code=hard_coded_agent.predefined_code)

    @classmethod
    def _get_chat_agent_details(
        cls,
        agent: AIAgent,
        prompt: PromptModel,
        settings: SettingsModel,
        repository: Session,
    ) -> ChatDetails:
        """
        Get chat agent details.
        """
        chat_agent = repository.get_one(ChatAgent, ChatAgent.id == agent.id)
        stopwords = chat_agent.stopwords
        return ChatDetails(
            prompt=prompt,
            settings=settings,
            stopwords=stopwords,
        )

    @classmethod
    def _get_critic_agent_details(
        cls,
        agent: AIAgent,
        prompt: PromptModel,
        settings: SettingsModel,
        repository: Session,
    ) -> CriticDetails:
        """
        Get critic agent details.
        """
        critic_agent = repository.get_one(CriticAgent, CriticAgent.id == agent.id)
        return CriticDetails(
            prompt=prompt,
            settings=settings,
            criticized_id=critic_agent.criticized_id,
        )

    @classmethod
    def _create_specific_agent(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> Agent:
        """
        Create specific agent.
        """
        details = data.details

        if data.agent_type in [AgentType.ai, AgentType.chat, AgentType.critic]:
            prompt = repository.get_one(Prompt, Prompt.id == details.prompt_id)
            if details.settings_id is not None:
                settings = repository.get_one(
                    Settings, Settings.id == details.settings_id
                )
                if (settings is None) or settings:
                    raise SettingsNotFoundError("Settings not found")

        if data.agent_type == AgentType.ai:
            return AIAgent(
                name=data.name,
                description=data.description,
                start_log_message=data.start_log_message,
                finish_log_message=data.finish_log_message,
                agent_type=data.agent_type,
                prompt=prompt,
                settings=settings,
                node_id=node_id,
            )

        elif data.agent_type == AgentType.chat:
            return ChatAgent(
                name=data.name,
                description=data.description,
                start_log_message=data.start_log_message,
                finish_log_message=data.finish_log_message,
                agent_type=data.agent_type,
                node_id=node_id,
            )

        elif data.agent_type == AgentType.critic:
            criticized = repository.get_one(
                Agent, Agent.id == data.details.criticized_id
            )
            if not criticized:
                raise CriticizedAgentNotFoundError("Criticized agent not found")

            return CriticAgent(
                name=data.name,
                description=data.description,
                start_log_message=data.start_log_message,
                finish_log_message=data.finish_log_message,
                agent_type=data.agent_type,
                criticized=criticized,
                node_id=node_id,
            )

        elif data.agent_type == AgentType.hard_code:
            return HardCodeAgent(
                name=data.name,
                description=data.description,
                start_log_message=data.start_log_message,
                finish_log_message=data.finish_log_message,
                agent_type=data.agent_type,
                predefined_type=data.details.predefined_type,
                node_id=node_id,
            )
