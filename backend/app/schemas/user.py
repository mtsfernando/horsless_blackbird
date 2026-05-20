"""Pydantic schemas for user-related requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime


class Token(BaseModel):
    """Schema for JWT access token response."""

    access_token: str
    token_type: str = "bearer"
