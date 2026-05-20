"""Player management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.player import Player
from app.models.user import User
from app.schemas.player import PlayerResponse, PlayerUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerResponse])
async def list_players(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Player]:
    """List all players.

    Args:
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        A list of all player profiles.
    """
    result = await db.execute(select(Player).order_by(Player.display_name))
    return list(result.scalars().all())


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Player:
    """Get a single player by ID.

    Args:
        player_id: The player's UUID.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        The player profile.
    """
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    return player


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: uuid.UUID,
    payload: PlayerUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Player:
    """Update a player's profile.

    Args:
        player_id: The player's UUID.
        payload: The fields to update.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        The updated player profile.
    """
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    if payload.display_name is not None:
        player.display_name = payload.display_name
    if payload.avatar_url is not None:
        player.avatar_url = payload.avatar_url

    await db.flush()
    await db.refresh(player)
    return player
