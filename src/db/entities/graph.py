from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Graph(Base):
    __tablename__ = "Graph"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="graphs")  # type: ignore
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="graph")  # type: ignore

    def __repr__(self):
        return f"Graph(id={self.id}, name={self.name}, description={self.description}, user_id={self.user_id})"
