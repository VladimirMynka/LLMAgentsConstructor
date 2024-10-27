from enum import Enum

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.document_template import DocumentTemplate
from src.db.entities.graph import Graph
from src.db.entities.input_documents import InputDocuments
from src.db.entities.required_document import RequiredDocument


class AgentType(Enum):
    ai = "ai"
    hard_coded = "hard_coded"
    chat = "chat"
    copying = "copying"
    critic = "critic"


class Agent(Base):
    __tablename__ = "Agent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    start_log_message: Mapped[str] = mapped_column(String, nullable=True)
    finish_log_message: Mapped[str] = mapped_column(String, nullable=True)

    graph_id: Mapped[int] = mapped_column(ForeignKey("Graph.id"), nullable=False)
    graph: Mapped[Graph] = relationship(Graph, back_populates="agents")

    output_documents: Mapped[list[DocumentTemplate]] = relationship(
        DocumentTemplate, back_populates="agent"
    )
    required_documents: Mapped[list[RequiredDocument]] = relationship(
        RequiredDocument, back_populates="agent"
    )
    input_documents: Mapped[list[InputDocuments]] = relationship(
        InputDocuments, back_populates="agent"
    )

    __mapper_args__ = {
        "polymorphic_identity": "agent",
        "polymorphic_on": agent_type,
    }

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
