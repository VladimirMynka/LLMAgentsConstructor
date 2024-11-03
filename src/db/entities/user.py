from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str]
    password_hash: Mapped[str]

    auth_tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user")  # type: ignore
    groups: Mapped[list["UserGroup"]] = relationship(back_populates="user")  # type: ignore

    def __repr__(self):
        return f"User(id={self.id}, login={self.login}, password_hash={self.password_hash})"
