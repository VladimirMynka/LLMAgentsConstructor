from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class RequiredDocument(Base):
    """Relationship many-to-many between Agent and required DocumentTemplate"""

    __tablename__ = "RequiredDocument"

    document_template_id: Mapped[int] = mapped_column(
        ForeignKey("DocumentTemplate.id"), primary_key=True
    )
    document_template: Mapped["DocumentTemplate"] = relationship(  # type: ignore
        "DocumentTemplate", back_populates="required"
    )

    agent_id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), primary_key=True)
    agent: Mapped["Agent"] = relationship("Agent", back_populates="required_documents")  # type: ignore

    def __repr__(self):
        return f"""
RequiredDocument(
    document_template_id={self.document_template_id}, 
    agent_id={self.agent_id}
)
"""
