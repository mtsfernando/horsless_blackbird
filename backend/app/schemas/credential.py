"""Pydantic schemas for credential-related requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CredentialCreate(BaseModel):
    """Schema for storing a new credential."""

    player_id: uuid.UUID
    provider: str = "18birdies"
    username: str
    password: str


class CredentialUpdate(BaseModel):
    """Schema for updating an existing credential."""

    username: str | None = None
    password: str | None = None


class CredentialResponse(BaseModel):
    """Schema for credential metadata — never exposes passwords."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_id: uuid.UUID
    provider: str
    last_scraped_at: datetime | None
    scrape_status: str
    created_at: datetime


class CredentialStatusResponse(BaseModel):
    """Schema for a player's credential status summary."""

    has_credentials: bool
    last_scraped_at: datetime | None = None
    scrape_status: str | None = None
