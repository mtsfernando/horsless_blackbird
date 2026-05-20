"""Player ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Player(Base):
    """A golf player — may or may not be linked to a registered user."""

    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="player", lazy="selectin"
    )
    rounds: Mapped[list["Round"]] = relationship(  # type: ignore[name-defined]
        "Round", back_populates="player", lazy="selectin"
    )
    credentials: Mapped[list["Credential"]] = relationship(  # type: ignore[name-defined]
        "Credential", back_populates="player", lazy="selectin", cascade="all, delete-orphan"
    )
