from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.agent import Agent


class DocumentTemplate(Base):
    __tablename__ = "DocumentTemplate"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    agent_id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), nullable=False)
    agent: Mapped[Agent] = relationship(Agent, back_populates="output_documents")

    def __repr__(self):
        return f"DocumentTemplate(id={self.id}, name={self.name}, filename={self.filename}, description={self.description}, agent_id={self.agent_id})"
