from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class ProviderGroup(Base):
    __tablename__ = "ProviderGroup"

    id: Mapped[int] = mapped_column(primary_key=True)

    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"), nullable=False)
    provider: Mapped["Provider"] = relationship("Provider", back_populates="provider_groups")  # type: ignore

    group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"), nullable=False)
    groups: Mapped["Group"] = relationship("Group", back_populates="provider_groups")  # type: ignore

    def __repr__(self):
        return f"""
ProviderGroup(
    id={self.id},
    provider_id={self.provider_id},
    group_id={self.group_id}
)
"""
