"""Round ORM model."""

import uuid
from datetime import date, datetime

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Round(Base):
    """A single round of golf played by a player."""

    __tablename__ = "rounds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tee_box: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_putts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_played: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    player: Mapped["Player"] = relationship(  # type: ignore[name-defined]
        "Player", back_populates="rounds", lazy="selectin"
    )
    hole_scores: Mapped[list["HoleScore"]] = relationship(  # type: ignore[name-defined]
        "HoleScore", back_populates="round", lazy="selectin", cascade="all, delete-orphan",
        order_by="HoleScore.hole_number"
    )

    @property
    def holes_count(self) -> int:
        """Count of played holes in this round."""
        return len(self.hole_scores)

