from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.chat_agent import ChatAgent


class Stopword(Base):
    __tablename__ = "Stopword"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("ChatAgent.id"), nullable=False, primary_key=True
    )
    word: Mapped[str] = mapped_column(String, nullable=False)

    agent: Mapped[ChatAgent] = relationship(ChatAgent, back_populates="stopwords")

    def __repr__(self):
        return f"Stopword(id={self.id}, word={self.word}, agent_id={self.agent_id})"
