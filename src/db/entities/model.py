from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


class Model(Base):
    __tablename__ = "Model"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"""
Model(
    id={self.id},
    owner={self.owner},
    name={self.name}
)
"""
