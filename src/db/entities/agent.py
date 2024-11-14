from enum import Enum

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class AgentType(Enum):
    ai = "ai"
    hard_coded = "hard_coded"
    chat = "chat"
    copying = "copying"
    critic = "critic"


class Agent(Base):
    __tablename__ = "Agent"

    id: Mapped[int] = mapped_column(primary_key=True)
    agent_type: Mapped[AgentType] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    start_log_message: Mapped[str] = mapped_column(nullable=True)
    finish_log_message: Mapped[str] = mapped_column(nullable=True)

    node_id: Mapped[int] = mapped_column(ForeignKey("Node.id"), nullable=False)

    node: Mapped["Node"] = relationship("Node")  # type: ignore

    output_documents: Mapped[list["DocumentTemplate"]] = relationship(  # type: ignore
        "DocumentTemplate", back_populates="agent"
    )
    required_documents: Mapped[list["RequiredDocument"]] = relationship(  # type: ignore
        "RequiredDocument", back_populates="agent"
    )
    input_documents: Mapped[list["InputDocuments"]] = relationship(  # type: ignore
        "InputDocuments", back_populates="agent"
    )

    __mapper_args__ = {
        "polymorphic_identity": "agent",
        "polymorphic_on": "agent_type",
    }

    __table_args__ = (UniqueConstraint("node_id", name="uix_agent_node_id"),)

    def __repr__(self):
        return f"""
Agent(
    id={self.id}, 
    name={self.name}, 
    type={self.agent_type}, 
    description={self.description}, 
    start_log_message={self.start_log_message}, 
    finish_log_message={self.finish_log_message}
)
"""
