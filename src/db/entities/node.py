from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Node(Base):
    __tablename__ = "Node"

    id: Mapped[int] = mapped_column(primary_key=True)
    graph_id: Mapped[int] = mapped_column(ForeignKey("Graph.id"), nullable=False)

    x: Mapped[int] = mapped_column(nullable=False)
    y: Mapped[int] = mapped_column(nullable=False)

    graph: Mapped["Graph"] = relationship("Graph", back_populates="nodes")  # type: ignore
    agent: Mapped["Agent" | None] = relationship("Agent", back_populates="node")  # type: ignore
    document_template: Mapped["DocumentTemplate" | None] = relationship(  # type: ignore
        "DocumentTemplate", back_populates="node"
    )

    def __repr__(self):
        return f"Node(id={self.id}, x={self.x}, y={self.y})"
