from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.document_template import DocumentTemplate
from src.db.entities.running import Running

class Document(Base):
    __tablename__ = "Document"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    template_id: Mapped[int] = mapped_column(
        ForeignKey("DocumentTemplate.id"), nullable=False
    )
    template: Mapped[DocumentTemplate] = relationship(
        DocumentTemplate, back_populates="documents"
    )
    
    running_id: Mapped[int] = mapped_column(
        ForeignKey("Running.id"), nullable=False
    )
    running: Mapped[Running] = relationship(Running, back_populates="documents")

    def __repr__(self):
        return (
            f"Document(id={self.id}, text={self.text}, template_id={self.template_id})"
        )
