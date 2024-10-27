from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base

class Model(Base):
    __tablename__ = 'Model'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    def __repr__(self):
        return f"""
Model(
    id={self.id},
    owner={self.owner},
    name={self.name}
)
"""
