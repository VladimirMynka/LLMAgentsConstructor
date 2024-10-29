from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Settings(Base):
    __tablename__ = "Settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("Model.id"), nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False, default=1.0)
    n: Mapped[int] = mapped_column(nullable=False, default=1)
    frequency_penalty: Mapped[float] = mapped_column(nullable=False, default=0.0)
    presence_penalty: Mapped[float] = mapped_column(nullable=False, default=0.0)

    model: Mapped["Model"] = relationship("Model")  # type: ignore

    def __repr__(self):
        return f"""
Settings(
    id={self.id},
    model_id={self.model_id},
    temperature={self.temperature},
    n={self.n},
    frequency_penalty={self.frequency_penalty},
    presence_penalty={self.presence_penalty}
)
"""
