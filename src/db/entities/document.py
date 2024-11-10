from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Document(Base):
    __tablename__ = "Document"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)
    creation_date: Mapped[datetime] = mapped_column(nullable=False)

    template_id: Mapped[int] = mapped_column(
        ForeignKey("DocumentTemplate.id"), nullable=False
    )
    template: Mapped["DocumentTemplate"] = relationship(  # type: ignore
        "DocumentTemplate", back_populates="documents"
    )

    running_id: Mapped[int] = mapped_column(ForeignKey("Running.id"), nullable=False)
    running: Mapped["Running"] = relationship("Running", back_populates="documents")  # type: ignore

    def __repr__(self):
        return (
            f"Document(id={self.id}, text={self.text}, template_id={self.template_id})"
        )
