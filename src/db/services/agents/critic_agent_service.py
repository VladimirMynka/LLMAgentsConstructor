from sqlalchemy.orm import Session

from src.db.entities.agent import Agent, AgentType
from src.db.entities.ai_agent import AIAgent
from src.db.entities.critic_agent import CriticAgent
from src.db.errors.agent import AgentNotFoundError, CriticizedAgentNotFoundError
from src.db.services.agents.ai_agent_service import AIAgentService
from src.db.services.agents.interfaces import ISpecificAgentService
from src.models.agent import CreateUpdateAgentModel
from src.models.agent_details import AIDetails, CriticDetails


class CriticAgentService(ISpecificAgentService):
    """Service for critic agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> CriticAgent:
        """
        Create critic agent entity. Additional method for creating critic agent.

        Args:
            data: CreateUpdateAgentModel - Agent data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session

        Returns:
            CriticAgent: CriticAgent model

        Raises:
            CriticizedAgentNotFoundError: If criticized agent not found
        """
        pre_entity = AIAgentService.make_entity(data, user_id, node_id, repository)

        details = data.details
        criticized_agent = cls._get_criticized_agent_from_request(
            details, pre_entity.node.graph_id, user_id, repository
        )

        entity = CriticAgent(
            agent_type=AgentType.critic,
            name=data.name,
            description=data.description,
            start_log_message=data.start_log_message,
            finish_log_message=data.finish_log_message,
            node_id=node_id,
            prompt_id=pre_entity.prompt_id,
            settings_id=pre_entity.settings_id,
            criticized_id=criticized_agent.id,
        )

        return entity

    @classmethod
    def get_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> CriticDetails:
        """
        Get critic agent details.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            repository: Session - Database session

        Returns:
            CriticDetails: CriticDetails model

        Raises:
            AgentNotFoundError: If agent not found
        """
        pre_model = AIAgentService.get_details(agent, user_id, repository)

        critic_agent = repository.get_one(CriticAgent, CriticAgent.id == agent.id)

        return CriticDetails(
            prompt=pre_model.prompt,
            settings=pre_model.settings,
            criticized_id=critic_agent.criticized_id,
        )

    @classmethod
    def update_agent(
        cls,
        agent: Agent,
        user_id: int,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> CriticAgent:
        """
        Update critic agent.
        """
        critic_agent = repository.get_one(CriticAgent, CriticAgent.id == agent.id)
        if not critic_agent:
            raise AgentNotFoundError("Critic agent not found")

        ai_agent = AIAgentService.update_agent(agent, user_id, data, repository)

        criticized = cls._get_criticized_agent_from_request(
            data.details, critic_agent.node.graph_id, user_id, repository
        )

        critic_agent.name = data.name
        critic_agent.description = data.description
        critic_agent.start_log_message = data.start_log_message
        critic_agent.finish_log_message = data.finish_log_message
        critic_agent.prompt = ai_agent.prompt
        critic_agent.settings = ai_agent.settings
        critic_agent.criticized = criticized

        return critic_agent

    @classmethod
    def delete_agent(
        cls,
        agent_id: int,
        repository: Session,
    ) -> None:
        """
        Delete critic agent.

        Args:
            agent_id: int - Agent id
            repository: Session - Database session

        Raises:
            AgentNotFoundError: If critic agent not found
        """
        critic_agent = repository.get_one(CriticAgent, CriticAgent.id == agent_id)
        if not critic_agent:
            raise AgentNotFoundError("Critic agent not found")

        repository.delete(critic_agent)

    @classmethod
    def _get_criticized_agent_from_request(
        cls,
        details: AIDetails,
        graph_id: int,
        user_id: int,
        repository: Session,
    ) -> AIAgent:
        """
        Get criticized agent from request.

        Args:
            details: AIDetails - Agent details
            graph_id: int - Graph id
            user_id: int - User id
            repository: Session - Database session

        Returns:
            AIAgent: AIAgent model

        Raises:
            CriticizedAgentNotFoundError: If criticized agent not found
        """
        try:
            agent = AIAgentService.get_agent_by_id(
                details.criticized_id,
                user_id,
                graph_id,
                repository,
            )
        except AgentNotFoundError:
            raise CriticizedAgentNotFoundError(
                f"Criticized agent with id {details.criticized_id} not found"
            )

        return agent
