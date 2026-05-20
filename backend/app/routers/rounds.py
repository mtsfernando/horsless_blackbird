"""Round endpoints — list rounds (paginated) and get round details."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.round import Round
from app.models.user import User
from app.schemas.round import RoundDetailResponse, RoundResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/rounds", tags=["rounds"])


@router.get("", response_model=list[RoundResponse])
async def list_rounds(
    player_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Round]:
    """List rounds with optional player filter and pagination.

    Args:
        player_id: Optional filter by player UUID.
        page: Page number (1-indexed).
        per_page: Number of results per page.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        A paginated list of rounds.
    """
    stmt = select(Round).order_by(Round.date_played.desc())

    if player_id is not None:
        stmt = stmt.where(Round.player_id == player_id)

    offset = (page - 1) * per_page
    stmt = stmt.offset(offset).limit(per_page)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{round_id}", response_model=RoundDetailResponse)
async def get_round(
    round_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Get a single round with hole-by-hole scores.

    Args:
        round_id: The round's UUID.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        The round data including all hole scores.
    """
    stmt = (
        select(Round)
        .where(Round.id == round_id)
        .options(selectinload(Round.hole_scores))
    )
    result = await db.execute(stmt)
    round_obj = result.scalar_one_or_none()

    if round_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Round not found",
        )

    return {
        "id": round_obj.id,
        "player_id": round_obj.player_id,
        "course_name": round_obj.course_name,
        "tee_box": round_obj.tee_box,
        "total_score": round_obj.total_score,
        "total_putts": round_obj.total_putts,
        "date_played": round_obj.date_played,
        "created_at": round_obj.created_at,
        "holes": round_obj.hole_scores,
    }
