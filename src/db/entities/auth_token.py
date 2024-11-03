import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class AuthToken(Base):
    __tablename__ = "AuthToken"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"))
    creation_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    expiration_date: Mapped[datetime.datetime] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="auth_token")  # type: ignore
