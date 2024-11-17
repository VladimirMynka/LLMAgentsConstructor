from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class UserGroup(Base):
    __tablename__ = "UserGroup"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.id"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Group.id"), nullable=False
    )

    owner: Mapped[bool] = mapped_column(default=False)
    change_members: Mapped[bool] = mapped_column(default=False)
    add_graphs: Mapped[bool] = mapped_column(default=False)
    run_graphs: Mapped[bool] = mapped_column(default=False)
    change_graphs_permissions: Mapped[bool] = mapped_column(default=False)
    delete_graphs: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="groups")  # type: ignore
    group: Mapped["Group"] = relationship(back_populates="members")  # type: ignore

    __table_args__ = (UniqueConstraint("user_id", "group_id"),)

    def __repr__(self):
        return (
            f"UserGroup(id={self.id}, user_id={self.user_id}, group_id={self.group_id})"
        )
