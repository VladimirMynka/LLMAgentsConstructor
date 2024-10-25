import asyncio

from openai import AsyncOpenAI

from src.core.agents.agent_parameters import (
    AgentParameters,
    AIAgentParameters,
    ChatAgentParameters,
    CriticAgentParameters,
    HardCodeAgentParameters,
)
from src.core.agents.agent_typings import DocumentsStore
from src.core.agents.agent_types.ai_agent import AIAgent
from src.core.agents.base_agent import BaseAgent
from src.core.agents.agent_types.chat_agent import ChatAgent
from src.core.agents.agent_types.critic_agent import CriticAgent
from src.core.agents.agent_types.hard_code_agent import HardCodeAgent


class Pipeline:
    def __init__(
        self,
        documents_store: DocumentsStore,
        client: AsyncOpenAI,
        **agents: AgentParameters,
    ):
        """Pipeline to run sequence of agents."""
        self._documents_store = documents_store
        self._client = client
        self._agents = {}

        for name, agent_parameters in agents.items():
            self._agents[name] = self._create_agent(name, agent_parameters)

    async def run(self) -> DocumentsStore:
        """Run pipeline."""
        await asyncio.gather(*[agent.run() for agent in self._agents.values()])
        return self._documents_store

    def _create_agent(self, name: str, agent_parameters: AgentParameters) -> BaseAgent:
        """Create agent by its parameters."""
        if isinstance(agent_parameters, CriticAgentParameters):
            criticized_agent = self._agents[agent_parameters.criticized_agent_name]
            kwargs = agent_parameters.to_dict()
            kwargs.pop("criticized_agent_name")
            return CriticAgent(
                criticized_agent=criticized_agent,
                client=self._client,
                name=name,
                documents_store=self._documents_store,
                **kwargs,
            )

        if isinstance(agent_parameters, ChatAgentParameters):
            return ChatAgent(
                client=self._client,
                name=name,
                documents_store=self._documents_store,
                **agent_parameters.to_dict(),
            )

        if isinstance(agent_parameters, AIAgentParameters):
            return AIAgent(
                client=self._client,
                name=name,
                documents_store=self._documents_store,
                **agent_parameters.to_dict(),
            )

        if isinstance(agent_parameters, HardCodeAgentParameters):
            return HardCodeAgent(
                name=name,
                documents_store=self._documents_store,
                **agent_parameters.to_dict(),
            )

        raise ValueError(f"Unknown agent type: {type(agent_parameters)}")
