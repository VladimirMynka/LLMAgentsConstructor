from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str]
    password_hash: Mapped[str]
    base_group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"), nullable=True)

    auth_tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user")  # type: ignore
    groups: Mapped[list["UserGroup"]] = relationship(back_populates="user")  # type: ignore

    base_group: Mapped["Group"] = relationship(back_populates="users")  # type: ignore

    def __repr__(self):
        return f"""
User(
    id={self.id},
    login={self.login},
    base_group_id={self.base_group_id},
    password_hash={self.password_hash}
)
"""
