from enum import Enum

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class PredefinedType(Enum, str):
    replace_text = "replace_text"


class HardCodeAgent(Base):
    __tablename__ = "HardCodeAgent"

    id: Mapped[int] = mapped_column(primary_key=True)
    predefined_type: Mapped[PredefinedType] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=True)
    arguments: Mapped[dict] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "HardCodeAgent",
    }
