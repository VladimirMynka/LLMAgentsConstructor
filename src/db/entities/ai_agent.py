from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.agents.agent_typings import GenerationSettings
from src.db.entities.agent import Agent
from src.db.entities.client import Client
from src.db.entities.prompt import Prompt


class AIAgent(Agent):
    __tablename__ = "AIAgent"

    id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), primary_key=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("Prompt.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("Client.id"), nullable=False)
    settings_id: Mapped[int] = mapped_column(
        ForeignKey("GenerationSettings.id"), nullable=False
    )

    prompt: Mapped[Prompt] = relationship("Prompt", back_populates="ai_agents")
    client: Mapped[Client] = relationship("Client", back_populates="ai_agents")
    settings: Mapped[GenerationSettings] = relationship(
        "GenerationSettings", back_populates="ai_agents"
    )

    __mapper_args__ = {
        "polymorphic_identity": "ai_agent",
    }

    def __repr__(self):
        return f"""
AIAgent(
    id={self.id},
    prompt={self.prompt},
    client_id={self.client_id}
)
"""
