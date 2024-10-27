from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.entities.ai_agent import AIAgent
from src.db.entities.stopwords import Stopword


class ChatAgent(AIAgent):
    __tablename__ = "ChatAgent"

    id: Mapped[int] = mapped_column(ForeignKey("AIAgent.id"), primary_key=True)
    stopwords: Mapped[list[Stopword]] = relationship(Stopword, back_populates="agent")

    __mapper_args__ = {
        "polymorphic_identity": "ChatAgent",
    }

    def __repr__(self):
        return f"ChatAgent(id={self.id}, stopwords={self.stopwords})"
