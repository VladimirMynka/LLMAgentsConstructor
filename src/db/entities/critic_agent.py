from sqlalchemy import ForeignKey, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.entities.ai_agent import AIAgent


class CriticAgent(AIAgent):
    __tablename__ = "CriticAgent"

    id: Mapped[int] = mapped_column(ForeignKey("AIAgent.id"), primary_key=True)
    criticized_id: Mapped[int] = mapped_column(ForeignKey("AIAgent.id"), nullable=False)

    criticized: Mapped["AIAgent"] = relationship("AIAgent")  # type: ignore

    __mapper_args__ = {
        "polymorphic_identity": "CriticAgent",
        "inherit_condition": and_(id == AIAgent.id),
    }

    def __repr__(self):
        return f"CriticAgent(id={self.id}, criticized_id={self.criticized_id})"
