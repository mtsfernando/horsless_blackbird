"""Pydantic schemas for player-related requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlayerCreate(BaseModel):
    """Schema for creating a new player."""

    display_name: str
    user_id: uuid.UUID | None = None


class PlayerUpdate(BaseModel):
    """Schema for updating a player."""

    display_name: str | None = None
    avatar_url: str | None = None


class PlayerResponse(BaseModel):
    """Schema for player data returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    display_name: str
    avatar_url: str | None
    created_at: datetime
