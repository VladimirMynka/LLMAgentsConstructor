from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Model(Base):
    __tablename__ = "Model"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"), nullable=False)
    provider: Mapped["Provider"] = relationship("Provider")  # type: ignore

    def __repr__(self):
        return f"""
Model(
    id={self.id},
    owner={self.owner},
    name={self.name},
    provider_id={self.provider_id}
)
"""
