from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class Prompt(Base):
    __tablename__ = "Prompt"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)

    groups: Mapped[list["GroupPrompt"]] = relationship(  # type: ignore
        "GroupPrompt", back_populates="prompt"
    )

    def __repr__(self):
        return f"""Prompt(
    id={self.id},
    name={self.name},
    text={self.text}
)"""
