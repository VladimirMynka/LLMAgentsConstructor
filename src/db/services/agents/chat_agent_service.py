from sqlalchemy.orm import Session

from src.db.entities.agent import Agent, AgentType
from src.db.entities.chat_agent import ChatAgent
from src.db.entities.stopwords import Stopword
from src.db.errors.agent import AgentNotFoundError
from src.db.services.agents.ai_agent_service import AIAgentService
from src.db.services.agents.interfaces import ISpecificAgentService
from src.models.agent import CreateUpdateAgentModel
from src.models.agent_details import ChatDetails


class ChatAgentService(ISpecificAgentService):
    """Service for chat agents."""

    @classmethod
    def make_entity(
        cls,
        data: CreateUpdateAgentModel,
        user_id: int,
        node_id: int,
        repository: Session,
    ) -> ChatAgent:
        """
        Create chat agent entity. Additional method for creating chat agent.

        Args:
            data: CreateUpdateAgentModel - Agent data
            user_id: int - User id
            node_id: int - Node id
            repository: Session - Database session

        Returns:
            ChatAgent: ChatAgent model
        """
        pre_entity = AIAgentService.make_entity(data, user_id, node_id, repository)

        entity = ChatAgent(
            agent_type=AgentType.chat,
            name=data.name,
            description=data.description,
            start_log_message=data.start_log_message,
            finish_log_message=data.finish_log_message,
            node_id=node_id,
            prompt_id=pre_entity.prompt_id,
            settings_id=pre_entity.settings_id,
        )

        stopwords = []

        for stopword in data.stopwords:
            stopword_entity = Stopword(
                word=stopword,
                agent_id=entity.id,
            )
            stopwords.append(stopword_entity)

        entity.stopwords = stopwords

        return entity

    @classmethod
    def get_details(
        cls,
        agent: Agent,
        user_id: int,
        repository: Session,
    ) -> ChatDetails:
        """
        Get chat agent details.

        Args:
            agent: Agent - Agent model
            user_id: int - User id
            repository: Session - Database session

        Returns:
            ChatDetails: ChatDetails model

        Raises:
            AgentNotFoundError: If agent not found
        """
        pre_model = AIAgentService.get_details(agent, user_id, repository)

        chat_agent = repository.get_one(ChatAgent, ChatAgent.id == agent.id)
        stopwords = chat_agent.stopwords

        return ChatDetails(
            prompt=pre_model.prompt,
            settings=pre_model.settings,
            stopwords=stopwords,
        )

    @classmethod
    def update_agent(
        cls,
        agent: Agent,
        user_id: int,
        data: CreateUpdateAgentModel,
        repository: Session,
    ) -> Agent:
        """
        Update chat agent.
        """
        chat_agent = repository.get_one(ChatAgent, ChatAgent.id == agent.id)
        if not chat_agent:
            raise AgentNotFoundError("Chat agent not found")

        ai_agent = AIAgentService.update_agent(agent, user_id, data, repository)

        for stopword in chat_agent.stopwords:
            repository.delete(stopword)

        chat_agent.stopwords = []

        stopwords = []
        for stopword in data.stopwords:
            stopword_entity = Stopword(
                word=stopword,
                agent_id=chat_agent.id,
            )
            stopwords.append(stopword_entity)

        chat_agent.name = data.name
        chat_agent.description = data.description
        chat_agent.start_log_message = data.start_log_message
        chat_agent.finish_log_message = data.finish_log_message
        chat_agent.prompt = ai_agent.prompt
        chat_agent.settings = ai_agent.settings
        chat_agent.stopwords = stopwords

        return chat_agent

    @classmethod
    def delete_agent(
        cls,
        agent_id: int,
        repository: Session,
    ) -> None:
        """
        Delete chat agent.
        """
        chat_agent = repository.get_one(ChatAgent, ChatAgent.id == agent_id)
        if not chat_agent:
            raise AgentNotFoundError("Chat agent not found")

        for stopword in chat_agent.stopwords:
            repository.delete(stopword)

        repository.delete(chat_agent)
