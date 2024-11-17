from abc import abstractmethod

from sqlalchemy.orm import Session

from src.db.entities.agent import Agent
from src.models.agent import CreateUpdateAgentModel
from src.models.agent_details import AgentDetails


class ISpecificAgentService:
    """Interface for specific agents."""

    @classmethod
    @abstractmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> Agent:
        """
        Create specific agent entity. Additional method for creating specific agent.

        Args:
            data: CreateUpdateAgentModel - Agent data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session

        Returns:
            Agent: Agent model
        """

    @classmethod
    @abstractmethod
    def get_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> AgentDetails:
        """
        Get agent details.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            repository: Session - Database session

        Returns:
            AgentDetails: Agent details

        Raises:
            AgentNotFoundError: If agent not found
        """

    @classmethod
    @abstractmethod
    def update_agent(
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
            Agent: Agent entity

        Raises:
            AgentNotFoundError: If agent not found
        """

    @classmethod
    @abstractmethod
    def delete_agent(
        cls,
        agent_id: int,
        repository: Session,
    ) -> None:
        """
        Delete agent.

        Args:
            agent_id: int - Agent id
            repository: Session - Database session

        Raises:
            AgentNotFoundError: If agent not found
        """
