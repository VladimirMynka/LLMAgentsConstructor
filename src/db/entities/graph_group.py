from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class GraphGroup(Base):
    __tablename__ = "GraphGroup"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    graph_id: Mapped[int] = mapped_column(
        ForeignKey("Graph.id"), nullable=False, primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Group.id"), nullable=False, primary_key=True
    )

    graph: Mapped["Graph"] = relationship("Graph", back_populates="groups")  # type: ignore
    group: Mapped["Group"] = relationship("Group", back_populates="graphs")  # type: ignore

    def __repr__(self):
        return f"GraphGroup(id={self.id}, name={self.name})"
