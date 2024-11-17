from sqlalchemy.orm import Session

from src.db.decorators import use_repository
from src.db.entities.agent import Agent, AgentType
from src.db.entities.node import Node
from src.db.errors.agent import AgentNotFoundError, InvalidAgentTypeError
from src.db.services.agents.ai_agent_service import AIAgentService
from src.db.services.agents.chat_agent_service import ChatAgentService
from src.db.services.agents.critic_agent_service import CriticAgentService
from src.db.services.agents.hard_code_agent_service import HardCodeAgentService
from src.db.services.agents.interfaces import ISpecificAgentService
from src.db.services.graph_service import GraphService
from src.db.services.user_service import UserService
from src.models.agent import CreateUpdateAgentModel, ExtendedAgentModel
from src.models.agent_details import AgentDetails
from src.models.node import ContentType, NodeModel

MAPPER: dict[AgentType, ISpecificAgentService] = {
    AgentType.ai: AIAgentService,
    AgentType.chat: ChatAgentService,
    AgentType.critic: CriticAgentService,
    AgentType.hard_code: HardCodeAgentService,
}


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
        agent_type: AgentType,
        data: CreateUpdateAgentModel,
        auth_token: str,
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
        repository.commit()

        return cls.get_agents(graph_id, auth_token, repository)

    @classmethod
    @use_repository
    def update_agent(
        cls,
        graph_id: int,
        agent_id: int,
        data: CreateUpdateAgentModel,
        auth_token: str,
        repository: Session,
    ) -> ExtendedAgentModel:
        """
        Update agent.

        Args:
            graph_id: int - Graph id
            agent_id: int - Agent id
            data: CreateUpdateAgentModel - Data
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
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        agent = repository.get_one(Agent, Agent.id == agent_id)
        if not agent:
            raise AgentNotFoundError("Agent not found")

        cls._update_specific_agent(agent, data, repository)
        repository.commit()

        return cls.get_agents(graph_id, auth_token, repository)

    @classmethod
    @use_repository
    def delete_agent(
        cls,
        agent_id: int,
        graph_id: int,
        auth_token: str,
        repository: Session,
    ) -> list[ExtendedAgentModel]:
        """
        Delete agent.

        Args:
            agent_id: int - Agent id
            graph_id: int - Graph id
            auth_token: str - Auth token
            repository: Session - Database session

        Returns:
            list[ExtendedAgentModel] - List of agents

        Raises:
            NotAuthorizedError: If the authentication token is invalid
            GraphNotFoundError: If the graph is not found or user has no access to it
            AgentNotFoundError: If the agent is not found
        """
        user_model = UserService.get_user_by_auth_token(auth_token, repository)
        GraphService.check_user_has_access_to_graph(user_model.id, graph_id)

        agent = repository.get_one(Agent, Agent.id == agent_id)
        if not agent:
            raise AgentNotFoundError("Agent not found")

        MAPPER[agent.agent_type].delete_agent(agent_id, repository)
        repository.delete(agent)
        repository.commit()

        return cls.get_agents(graph_id, auth_token, repository)

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
    ) -> AgentDetails:
        """
        Get agent details.

        Args:
            agent: Agent - Agent
            user_id: int - User id
            repository: Session - Database session

        Returns:
            AgentDetails - Agent details

        Raises:
            InvalidAgentTypeError: If the agent type is invalid
        """
        if agent.agent_type not in MAPPER:
            raise InvalidAgentTypeError("Invalid agent type")

        return MAPPER[agent.agent_type].get_details(agent, user_id, repository)

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

        Args:
            data: CreateUpdateAgentModel - Data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session

        Returns:
            Agent - Agent

        Raises:
            InvalidAgentTypeError: If the agent type is invalid
        """
        if data.agent_type not in MAPPER:
            raise InvalidAgentTypeError("Invalid agent type")

        return MAPPER[data.agent_type].make_entity(data, user_id, node_id, repository)

    @classmethod
    def _update_specific_agent(
        cls,
        agent: Agent,
        user_id: int,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> Agent:
        """
        Update specific agent.

        Args:
            agent: Agent - Agent
            user_id: int - User id
            data: CreateUpdateAgentModel - Data
            repository: Session - Database session

        Returns:
            Agent - Agent entity

        Raises:
            InvalidAgentTypeError: If the agent type is invalid
            AgentNotFoundError: If agent not found
        """
        if agent.agent_type not in MAPPER:
            raise InvalidAgentTypeError("Invalid agent type")

        return MAPPER[agent.agent_type].update_agent(agent, user_id, data, repository)
