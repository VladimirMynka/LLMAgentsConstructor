from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class ProviderToken(Base):
    __tablename__ = "ProviderToken"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"))
    token: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User")  # type: ignore
    provider: Mapped["Provider"] = relationship("Provider")  # type: ignore

    __table_args__ = (UniqueConstraint("user_id", "provider_id"),)

    def __repr__(self):
        return f"""
ProviderToken(
    id={self.id},
    user_id={self.user_id},
    provider_id={self.provider_id},
    token={self.token}
)
"""
