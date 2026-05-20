"""Profile endpoints — manage own profile, nickname, and credentials."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.credential import Credential
from app.models.player import Player
from app.models.user import User
from app.schemas.credential import CredentialStatusResponse, CredentialUpdate
from app.schemas.player import PlayerResponse, PlayerUpdate
from app.services import credential_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


async def _get_player_for_user(db: AsyncSession, user: User) -> Player:
    """Helper to fetch the Player linked to a User, or raise 404."""
    result = await db.execute(select(Player).where(Player.user_id == user.id))
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No player profile found for this user",
        )
    return player


@router.get("", response_model=PlayerResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Player:
    """Get the current user's player profile.

    Args:
        current_user: The authenticated user.
        db: The async database session.

    Returns:
        The user's player profile including display_name and avatar.
    """
    return await _get_player_for_user(db, current_user)


@router.put("", response_model=PlayerResponse)
async def update_profile(
    payload: PlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Player:
    """Update the current user's display name or avatar.

    Args:
        payload: The fields to update.
        current_user: The authenticated user.
        db: The async database session.

    Returns:
        The updated player profile.
    """
    player = await _get_player_for_user(db, current_user)

    if payload.display_name is not None:
        player.display_name = payload.display_name
    if payload.avatar_url is not None:
        player.avatar_url = payload.avatar_url

    await db.flush()
    await db.refresh(player)
    return player


@router.get("/credentials", response_model=CredentialStatusResponse)
async def get_credential_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get the current user's credential status (no passwords returned).

    Args:
        current_user: The authenticated user.
        db: The async database session.

    Returns:
        Credential status summary.
    """
    player = await _get_player_for_user(db, current_user)
    result = await db.execute(
        select(Credential).where(Credential.player_id == player.id)
    )
    cred = result.scalar_one_or_none()

    if cred is None:
        return {"has_credentials": False}

    return {
        "has_credentials": True,
        "last_scraped_at": cred.last_scraped_at,
        "scrape_status": cred.scrape_status,
    }


@router.put("/credentials", response_model=CredentialStatusResponse)
async def set_credentials(
    payload: CredentialUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Set or update the current user's 18Birdies credentials.

    Args:
        payload: The credential data to store (username, password).
        current_user: The authenticated user.
        db: The async database session.

    Returns:
        Updated credential status.
    """
    player = await _get_player_for_user(db, current_user)

    # Check if credential already exists
    result = await db.execute(
        select(Credential).where(
            Credential.player_id == player.id,
            Credential.provider == "18birdies",
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        await credential_service.update_credential(
            db, existing.id, payload.username, payload.password
        )
    else:
        if payload.username is None or payload.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both username and password are required for initial setup",
            )
        await credential_service.store_credential(
            db, player.id, "18birdies", payload.username, payload.password
        )

    return {
        "has_credentials": True,
        "last_scraped_at": None,
        "scrape_status": "pending",
    }


@router.delete("/credentials", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credentials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove the current user's 18Birdies credentials.

    Args:
        current_user: The authenticated user.
        db: The async database session.
    """
    player = await _get_player_for_user(db, current_user)
    result = await db.execute(
        select(Credential).where(
            Credential.player_id == player.id,
            Credential.provider == "18birdies",
        )
    )
    cred = result.scalar_one_or_none()
    if cred:
        await credential_service.delete_credential(db, cred.id)


@router.post("/credentials/test", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def test_credentials(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Test the current user's credentials — placeholder.

    Args:
        current_user: The authenticated user.

    Returns:
        A 501 status with a message.
    """
    return {"detail": "Credential testing not yet implemented"}


@router.post("/refresh", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def refresh_data(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Trigger a data refresh via SSE — placeholder for Phase 2.

    Args:
        current_user: The authenticated user.

    Returns:
        A 501 status with a message.
    """
    return {"detail": "SSE refresh not yet implemented — coming in Phase 2"}
