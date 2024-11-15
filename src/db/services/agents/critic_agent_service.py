from sqlalchemy.orm import Session

from src.db.entities.agent import AgentType
from src.db.entities.critic_agent import CriticAgent
from src.db.services.agents.ai_agent_service import AIAgentService
from src.models.agent import CreateUpdateAgentModel


class CriticAgentService:
    """Service for critic agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> CriticAgent:
        """Create critic agent entity. Additional method for creating critic agent."""
        pre_entity = AIAgentService.make_entity(data, user_id, node_id, repository)

        details = data.details
        criticized_agent = cls._get_criticized_agent_from_request(
            details, user_id, repository
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
            criticized_id=pre_entity.id,
        )

        return entity
