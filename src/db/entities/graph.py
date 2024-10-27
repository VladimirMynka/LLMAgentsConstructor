from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.user import User


class Graph(Base):
    __tablename__ = "Graph"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)

    user: Mapped[User] = relationship(User, back_populates="graphs")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="graph") # type: ignore

    def __repr__(self):
        return f"Graph(id={self.id}, name={self.name}, description={self.description}, user_id={self.user_id})"
