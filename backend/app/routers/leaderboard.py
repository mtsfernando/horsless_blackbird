"""Leaderboard endpoints — aggregate stats across players."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, nulls_last
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.player import Player
from app.models.round import Round
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
async def get_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get the leaderboard — players ranked by average score.

    Args:
        limit: Maximum number of players to return.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        A list of players with their average scores, ordered ascending.
    """
    stmt = (
        select(
            Player.id,
            Player.display_name,
            Player.avatar_url,
            func.count(Round.id).label("rounds_played"),
            func.avg(Round.total_score).label("avg_score"),
            func.min(Round.total_score).label("best_score"),
        )
        .outerjoin(Round, Round.player_id == Player.id)
        .group_by(Player.id, Player.display_name, Player.avatar_url)
        .order_by(nulls_last(func.avg(Round.total_score).asc()))
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "player_id": row.id,
            "display_name": row.display_name,
            "avatar_url": row.avatar_url,
            "rounds_played": row.rounds_played,
            "avg_score": round(float(row.avg_score), 1) if row.avg_score else None,
            "best_score": row.best_score,
        }
        for row in rows
    ]


@router.get("/stats")
async def get_leaderboard_stats(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Get aggregate leaderboard statistics.

    Args:
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        Summary statistics across all players and rounds.
    """
    # Total players
    player_count_result = await db.execute(select(func.count(Player.id)))
    total_players = player_count_result.scalar() or 0

    # Total rounds
    round_count_result = await db.execute(select(func.count(Round.id)))
    total_rounds = round_count_result.scalar() or 0

    # Overall average score
    avg_result = await db.execute(select(func.avg(Round.total_score)))
    overall_avg = avg_result.scalar()

    return {
        "total_players": total_players,
        "total_rounds": total_rounds,
        "overall_avg_score": round(float(overall_avg), 1) if overall_avg else None,
    }
