from sqlalchemy import ForeignKey, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.entities.agent import Agent


class CopyingAgent(Agent):
    __tablename__ = "CopyingAgent"

    id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), primary_key=True)
    base_agent_id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), nullable=False)

    base_agent: Mapped["Agent"] = relationship("Agent")  # type: ignore

    __mapper_args__ = {
        "polymorphic_identity": "CopyingAgent",
        "inherit_condition": and_(id == Agent.id),
    }

    def __repr__(self):
        return f"CopyingAgent(id={self.id}, base_agent_id={self.base_agent_id})"
