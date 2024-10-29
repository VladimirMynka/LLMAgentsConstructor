from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class UserToken(Base):
    __tablename__ = "UserToken"

    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("Client.id"), primary_key=True)
    token: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User")  # type: ignore
    client: Mapped["Client"] = relationship("Client")  # type: ignore

    def __repr__(self):
        return f"""
UserToken(
    user_id={self.user_id},
    client_id={self.client_id},
    token={self.token}
)
"""
