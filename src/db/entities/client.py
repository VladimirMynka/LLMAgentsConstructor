from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class Client(Base):
    __tablename__ = "Client"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"""
Client(
    id={self.id},
    url={self.url}
)
"""
