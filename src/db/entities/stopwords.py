from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Stopword(Base):
    __tablename__ = "Stopword"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("ChatAgent.id"), nullable=False, primary_key=True
    )
    word: Mapped[str] = mapped_column(nullable=False)

    agent: Mapped["ChatAgent"] = relationship("ChatAgent", back_populates="stopwords")  # type: ignore

    def __repr__(self):
        return f"Stopword(id={self.id}, word={self.word}, agent_id={self.agent_id})"
