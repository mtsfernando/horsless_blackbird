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
    # Fetch all players
    result = await db.execute(select(Player))
    players = result.scalars().all()

    leaderboard_data = []
    for player in players:
        scores = []
        for r in player.rounds:
            score = r.total_score
            num_holes = len(r.hole_scores)
            if num_holes < 18:
                score = score * 2
            scores.append(score)

        avg_score = sum(scores) / len(scores) if scores else None
        best_score = min(scores) if scores else None

        leaderboard_data.append({
            "player_id": player.id,
            "display_name": player.display_name,
            "avatar_url": player.avatar_url,
            "rounds_played": len(player.rounds),
            "avg_score": round(float(avg_score), 1) if avg_score is not None else None,
            "best_score": best_score,
        })

    # Sort leaderboard_data: players with rounds first (avg_score not None) ordered by avg_score ascending,
    # then players with no rounds (avg_score is None).
    leaderboard_data.sort(
        key=lambda x: (x["avg_score"] is None, x["avg_score"] if x["avg_score"] is not None else 0)
    )

    return leaderboard_data[:limit]


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

    # Fetch all rounds to compute 18-hole equivalent average
    result = await db.execute(select(Round))
    rounds = result.scalars().all()
    total_rounds = len(rounds)

    scores = []
    for r in rounds:
        score = r.total_score
        num_holes = len(r.hole_scores)
        if num_holes < 18:
            score = score * 2
        scores.append(score)

    overall_avg = sum(scores) / len(scores) if scores else None

    return {
        "total_players": total_players,
        "total_rounds": total_rounds,
        "overall_avg_score": round(float(overall_avg), 1) if overall_avg is not None else None,
    }
