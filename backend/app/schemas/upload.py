"""Pydantic schemas for upload-related responses."""

import uuid

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Schema for the result of a file upload."""

    id: uuid.UUID
    status: str
    rounds_imported: int
    message: str
