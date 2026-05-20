"""RawImport ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RawImport(Base):
    """A raw data import record from a scraper or manual upload."""

    __tablename__ = "raw_imports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="'scraper' or 'manual_upload'"
    )
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending",
        comment="'pending', 'processed', or 'failed'"
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="raw_imports", lazy="selectin"
    )
