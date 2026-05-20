"""HoleScore ORM model."""

import uuid

from sqlalchemy import Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HoleScore(Base):
    """Score data for a single hole within a round."""

    __tablename__ = "hole_scores"
    __table_args__ = (
        UniqueConstraint("round_id", "hole_number", name="uq_round_hole"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    round_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hole_number: Mapped[int] = mapped_column(Integer, nullable=False)
    par: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    putts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fairway_hit: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    gir: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Relationships
    round: Mapped["Round"] = relationship(  # type: ignore[name-defined]
        "Round", back_populates="hole_scores", lazy="selectin"
    )
