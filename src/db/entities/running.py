from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.entities.graph import Graph

class RunningStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"


class Running(Base):
    __tablename__ = "Running"

    id: Mapped[int] = mapped_column(primary_key=True)
    graph_id: Mapped[int] = mapped_column(ForeignKey(Graph.id))
    graph: Mapped[Graph] = relationship(Graph, back_populates="running")
    status: Mapped[RunningStatus] = mapped_column(nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="running") # type: ignore

    def __repr__(self):
        return f"Running(id={self.id}, graph_id={self.graph_id})"
