from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str]
    password_hash: Mapped[str]

    def __repr__(self):
        return f"User(id={self.id}, login={self.login}, password_hash={self.password_hash})"
