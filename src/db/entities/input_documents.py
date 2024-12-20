from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class InputDocuments(Base):
    __tablename__ = "InputDocuments"

    document_template_id: Mapped[int] = mapped_column(
        ForeignKey("DocumentTemplate.id"), primary_key=True
    )
    document_template: Mapped["DocumentTemplate"] = relationship(  # type: ignore
        "DocumentTemplate", back_populates="input"
    )

    agent_id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), primary_key=True)
    agent: Mapped["Agent"] = relationship("Agent", back_populates="input_documents")  # type: ignore

    def __repr__(self):
        return f"""
InputDocuments(
    document_template_id={self.document_template_id}, 
    agent_id={self.agent_id}
)
"""
