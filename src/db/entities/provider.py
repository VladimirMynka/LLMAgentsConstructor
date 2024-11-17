from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Provider(Base):
    __tablename__ = "Provider"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    provider_groups: Mapped[list["ProviderGroup"]] = relationship(back_populates="provider")  # type: ignore
    models: Mapped[list["Model"]] = relationship(back_populates="provider")  # type: ignore

    def __repr__(self):
        return f"""
Provider(
    id={self.id},
    url={self.url},
    name={self.name}
)
"""
