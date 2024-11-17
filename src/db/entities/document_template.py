from xml.dom.minidom import Document

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class DocumentTemplate(Base):
    __tablename__ = "DocumentTemplate"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    node_id: Mapped[int] = mapped_column(ForeignKey("Node.id"), nullable=False)
    node: Mapped["Node"] = relationship("Node")  # type: ignore

    agent_id: Mapped[int] = mapped_column(ForeignKey("Agent.id"), nullable=False)
    agent: Mapped["Agent"] = relationship("Agent", back_populates="output_documents")  # type: ignore

    instances: Mapped[list["Document"]] = relationship(
        "Document", back_populates="template"
    )

    __table_args__ = (
        UniqueConstraint("node_id", name="uix_document_template_node_id"),
    )

    def __repr__(self):
        return f"""DocumentTemplate(
            id={self.id}, 
            name={self.name}, 
            filename={self.filename}, 
            description={self.description},
            node_id={self.node_id},
            agent_id={self.agent_id}
        )"""
