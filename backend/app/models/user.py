"""User ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """A registered user of the application."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    player: Mapped["Player"] = relationship(  # type: ignore[name-defined]
        "Player", back_populates="user", uselist=False, lazy="selectin"
    )
    raw_imports: Mapped[list["RawImport"]] = relationship(  # type: ignore[name-defined]
        "RawImport", back_populates="user", lazy="selectin"
    )

    @property
    def display_name(self) -> str | None:
        """Get the display name from the linked player profile."""
        return self.player.display_name if self.player else None
