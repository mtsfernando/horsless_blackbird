"""Activity router — combine round and social activity feed."""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.player import Player
from app.models.round import Round
from app.models.raw_import import RawImport
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.routers.profile import _get_player_for_user

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("")
async def get_activity_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get a unified timeline of recent player activities (rounds & social connection announcements)."""
    # Fetch player
    player = await _get_player_for_user(db, current_user)

    round_activities = []
    for r in player.rounds:
        dt_played = datetime(r.date_played.year, r.date_played.month, r.date_played.day)
        date_str = dt_played.isoformat() + "Z"
        
        round_activities.append({
            "type": "round",
            "id": str(r.id),
            "date": date_str,
            "course": r.course_name,
            "score": r.total_score,
            "holes": len(r.hole_scores),
            "putts": r.total_putts,
            "scorecard": [hs.score for hs in r.hole_scores],
            "pars": [hs.par for hs in r.hole_scores]
        })

    # Fetch user's latest RawImport to parse social connection announcements
    stmt = (
        select(RawImport)
        .where(RawImport.user_id == current_user.id)
        .order_by(RawImport.imported_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    latest_import = result.scalar_one_or_none()

    social_activities = []
    if latest_import and latest_import.raw_json:
        try:
            feed_data = latest_import.raw_json.get("myData", {}).get("feedData", {})
            messages = feed_data.get("messages", [])
            for msg in messages:
                content = msg.get("content")
                msg_id = msg.get("messageId")
                if content and msg_id:
                    try:
                        u = uuid.UUID(msg_id)
                        # Extract exact creation timestamp from UUID v1
                        timestamp = (u.time - 0x01b21dd213814000) / 1e7
                        dt = datetime.utcfromtimestamp(timestamp)
                        date_str = dt.isoformat() + "Z"
                    except Exception:
                        date_str = datetime.utcnow().isoformat() + "Z"
                        
                    social_activities.append({
                        "type": "social",
                        "id": msg_id,
                        "date": date_str,
                        "content": content
                    })
        except Exception as e:
            # Silently log/print and continue rather than failing the whole feed
            print(f"Error parsing social messages from raw import: {e}")

    combined = round_activities + social_activities
    combined.sort(key=lambda x: x["date"], reverse=True)
    return combined
