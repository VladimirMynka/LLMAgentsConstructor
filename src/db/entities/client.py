from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class Client(Base):
    __tablename__ = "Client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"""
Client(
    id={self.id},
    url={self.url}
)
"""
