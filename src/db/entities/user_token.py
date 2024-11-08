from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class UserToken(Base):
    __tablename__ = "UserToken"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("UserGroup.id"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("Provider.id"))
    token: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["UserGroup"] = relationship("UserGroup")  # type: ignore
    provider: Mapped["Provider"] = relationship("Provider")  # type: ignore

    __table_args__ = (UniqueConstraint("user_id", "provider_id"),)

    def __repr__(self):
        return f"""
UserToken(
    id={self.id},
    user_id={self.user_id},
    provider_id={self.provider_id},
    token={self.token}
)
"""
