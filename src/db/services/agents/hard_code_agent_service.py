from sqlalchemy.orm import Session

from src.db.entities.agent import Agent, AgentType
from src.db.entities.hard_code_agent import HardCodeAgent
from src.db.errors.agent import AgentNotFoundError
from src.db.services.agents.interfaces import ISpecificAgentService
from src.models.agent import CreateUpdateAgentModel
from src.models.agent_details import HardCodeDetails


class HardCodeAgentService(ISpecificAgentService):
    """Service for hard code agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> HardCodeAgent:
        """
        Create hard code agent entity. Additional method for creating hard code agent.

        Args:
            data: CreateUpdateAgentModel - Agent data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session (unused)

        Returns:
            HardCodeAgent: HardCodeAgent model
        """
        entity = HardCodeAgent(
            agent_type=AgentType.hard_code,
            name=data.name,
            description=data.description,
            start_log_message=data.start_log_message,
            finish_log_message=data.finish_log_message,
            predefined_type=data.predefined_type,
            url=data.url,
            arguments=data.arguments,
            node_id=node_id,
        )

        return entity

    @classmethod
    def get_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> HardCodeDetails:
        """
        Get hard code agent details.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            repository: Session - Database session

        Returns:
            HardCodeDetails: HardCodeDetails model
        """
        hard_coded_agent = repository.get_one(
            HardCodeAgent, HardCodeAgent.id == agent.id
        )
        return HardCodeDetails(predefined_code=hard_coded_agent.predefined_code)

    @classmethod
    def update_agent(
        cls,
        agent: Agent,
        user_id: int,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> HardCodeAgent:
        """
        Update hard code agent.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            data: CreateUpdateAgentModel - Agent data
            repository: Session - Database session

        Returns:
            HardCodeAgent: HardCodeAgent model

        Raises:
            AgentNotFoundError: If hard code agent not found
        """
        hard_coded_agent = repository.get_one(
            HardCodeAgent, HardCodeAgent.id == agent.id
        )
        if not hard_coded_agent:
            raise AgentNotFoundError("Hard code agent not found")

        hard_coded_agent.name = data.name
        hard_coded_agent.description = data.description
        hard_coded_agent.start_log_message = data.start_log_message
        hard_coded_agent.finish_log_message = data.finish_log_message
        hard_coded_agent.predefined_type = data.details.predefined_type
        hard_coded_agent.url = data.details.url
        hard_coded_agent.arguments = data.details.arguments

        return hard_coded_agent

    @classmethod
    def delete_agent(
        cls,
        agent_id: int,
        repository: Session,
    ) -> None:
        """
        Delete hard code agent.

        Args:
            agent_id: int - Agent id
            repository: Session - Database session

        Raises:
            AgentNotFoundError: If hard code agent not found
        """
        hard_coded_agent = repository.get_one(
            HardCodeAgent, HardCodeAgent.id == agent_id
        )
        if not hard_coded_agent:
            raise AgentNotFoundError("Hard code agent not found")

        repository.delete(hard_coded_agent)
