from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class UserGroup(Base):
    __tablename__ = "UserGroup"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.id"), nullable=False, primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Group.id"), nullable=False, primary_key=True
    )

    owner: Mapped[bool] = mapped_column(default=False)
    add_users: Mapped[bool] = mapped_column(default=False)
    edit_users_permissions: Mapped[bool] = mapped_column(default=False)
    delete_users: Mapped[bool] = mapped_column(default=False)
    add_graphs: Mapped[bool] = mapped_column(default=False)
    edit_graphs_permissions: Mapped[bool] = mapped_column(default=False)
    delete_graphs: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="groups")  # type: ignore
    group: Mapped["Group"] = relationship(back_populates="users")  # type: ignore

    def __repr__(self):
        return (
            f"UserGroup(id={self.id}, user_id={self.user_id}, group_id={self.group_id})"
        )
