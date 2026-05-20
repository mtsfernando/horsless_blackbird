"""Credential ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Credential(Base):
    """Encrypted third-party credentials for a player (e.g. 18Birdies)."""

    __tablename__ = "credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="18birdies")
    username_enc: Mapped[str] = mapped_column(String(500), nullable=False)
    password_enc: Mapped[str] = mapped_column(String(500), nullable=False)
    last_scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scrape_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="'pending', 'success', 'failed', or 'disabled'"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    player: Mapped["Player"] = relationship(  # type: ignore[name-defined]
        "Player", back_populates="credentials", lazy="selectin"
    )
