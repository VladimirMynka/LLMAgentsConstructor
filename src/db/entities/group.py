from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Group(Base):
    __tablename__ = "Group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    users: Mapped[list["UserGroup"]] = relationship(back_populates="group")  # type: ignore
    graphs: Mapped[list["GraphGroup"]] = relationship(back_populates="group")  # type: ignore

    def __repr__(self):
        return f"Group(id={self.id}, name={self.name})"
