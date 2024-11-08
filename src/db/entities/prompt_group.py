from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


class PromptGroup(Base):
    __tablename__ = "PromptGroup"

    id: Mapped[int] = mapped_column(primary_key=True)

    prompt_id: Mapped[int] = mapped_column(ForeignKey("Prompt.id"), nullable=False)
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="prompt_groups")  # type: ignore

    group_id: Mapped[int] = mapped_column(ForeignKey("Group.id"), nullable=False)
    group: Mapped["Group"] = relationship("Group", back_populates="prompt_groups")  # type: ignore

    __table_args__ = (
        UniqueConstraint("prompt_id", "group_id", name="prompt_group_unique"),
    )

    def __repr__(self):
        return f"""PromptGroup(
    id={self.id},
    prompt_id={self.prompt_id},
    group_id={self.group_id}
)"""
