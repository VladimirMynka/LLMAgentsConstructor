from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.entities.agent import Agent


class AIAgent(Agent):
    __tablename__ = "AIAgent"

    id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), primary_key=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("Prompt.id"), nullable=False)
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"), nullable=False)
    settings_id: Mapped[int] = mapped_column(ForeignKey("Settings.id"), nullable=False)

    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="ai_agents")  # type: ignore
    provider: Mapped["Provider"] = relationship("Provider", back_populates="ai_agents")  # type: ignore
    settings: Mapped["Settings"] = relationship("Settings", back_populates="ai_agents")  # type: ignore

    __mapper_args__ = {
        "polymorphic_identity": "ai_agent",
    }

    def __repr__(self):
        return f"""
AIAgent(
    id={self.id},
    prompt={self.prompt},
    provider_id={self.provider_id}
)
"""
