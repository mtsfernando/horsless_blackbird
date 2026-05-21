"""Pydantic schemas for round and hole-score responses."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HoleScoreResponse(BaseModel):
    """Schema for a single hole's score data."""

    model_config = ConfigDict(from_attributes=True)

    hole_number: int
    par: int
    score: int
    putts: int | None
    fairway_hit: bool | None
    gir: bool | None


class RoundResponse(BaseModel):
    """Schema for round summary data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_id: uuid.UUID
    course_name: str
    tee_box: str | None
    total_score: int
    total_putts: int | None
    date_played: date
    created_at: datetime
    holes_count: int = 18



class RoundDetailResponse(RoundResponse):
    """Schema for round data including hole-by-hole scores."""

    holes: list[HoleScoreResponse] = []
