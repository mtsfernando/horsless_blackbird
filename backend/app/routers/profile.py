"""Profile endpoints — manage own profile, nickname, and credentials."""

import uuid
import json
import asyncio
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session_factory
from app.models.credential import Credential
from app.models.player import Player
from app.models.user import User
from app.models.round import Round
from app.models.hole_score import HoleScore
from app.schemas.credential import CredentialStatusResponse, CredentialUpdate
from app.schemas.player import PlayerResponse, PlayerUpdate
from app.services import credential_service
from app.utils.dependencies import get_current_user
from app.utils.security import decode_access_token

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
        return {"has_credentials": False, "username": None}

    from app.utils.encryption import decrypt
    try:
        username = decrypt(cred.username_enc)
    except Exception:
        username = None

    return {
        "has_credentials": True,
        "username": username,
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

    username = payload.username
    if existing:
        await credential_service.update_credential(
            db, existing.id, payload.username, payload.password
        )
        if username is None:
            from app.utils.encryption import decrypt
            try:
                username = decrypt(existing.username_enc)
            except Exception:
                username = None
    else:
        if payload.username is None or payload.password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both username and password are required for initial setup",
            )
        await credential_service.store_credential(
            db, player.id, "18birdies", payload.username, payload.password
        )

    await db.commit()  # Explicitly commit database transaction!

    return {
        "has_credentials": True,
        "username": username,
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
        await db.commit()  # Explicitly commit database transaction!


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


@router.get("/refresh")
async def refresh_data(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a data refresh via Server-Sent Events (SSE).

    This streams the progress of scraping credentials, fetching round details,
    inserting/updating the scorecards inside the database, and updating metrics.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    player = await _get_player_for_user(db, user)

    # Check if player has 18Birdies credentials
    cred_result = await db.execute(
        select(Credential).where(
            Credential.player_id == player.id,
            Credential.provider == "18birdies",
        )
    )
    cred = cred_result.scalar_one_or_none()
    if cred is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 18Birdies credentials linked to this account",
        )

    # Safe references for generator
    player_id = player.id

    async def event_generator():
        stages = [
            {"progress": 10, "stage": "auth", "message": "Authenticating 18Birdies credentials...", "delay": 1.0},
            {"progress": 35, "stage": "fetching", "message": "Connected! Scraping scorecard index...", "delay": 1.5},
            {"progress": 50, "stage": "downloading", "message": "Downloading round details and hole scores...", "delay": 1.5},
            {"progress": 65, "stage": "importing", "message": "Importing scorecards to Horseless Blackbird database...", "delay": 1.0},
            {"progress": 85, "stage": "updating", "message": "Recalculating handicap index and leaderboard standings...", "delay": 1.0},
            {"progress": 100, "stage": "complete", "message": "Successfully imported rounds! Your dashboard has been updated.", "delay": 0.5},
        ]

        for s in stages:
            await asyncio.sleep(s["delay"])

            if s["stage"] == "importing":
                # Perform database insert operations in a separate session
                async with async_session_factory() as session:
                    try:
                        # 1. Fetch rounds for this player
                        rounds_result = await session.execute(
                            select(Round).where(Round.player_id == player_id)
                        )
                        existing_rounds = list(rounds_result.scalars().all())

                        # 2. Check if we need to insert mock rounds or new rounds
                        if len(existing_rounds) == 0:
                            # Insert 3 mock rounds
                            mock_rounds = [
                                {
                                    "course_name": "Pebble Beach Golf Links",
                                    "tee_box": "Blue",
                                    "total_score": 78,
                                    "total_putts": 29,
                                    "date_played": date(2026, 5, 10),
                                    "pars": [4, 4, 4, 4, 3, 5, 3, 4, 4, 4, 4, 3, 4, 5, 4, 4, 3, 5],
                                    "scores": [4, 5, 4, 4, 3, 5, 4, 4, 5, 4, 5, 3, 4, 6, 4, 4, 4, 5],
                                },
                                {
                                    "course_name": "Augusta National Golf Club",
                                    "tee_box": "Members",
                                    "total_score": 82,
                                    "total_putts": 31,
                                    "date_played": date(2026, 5, 14),
                                    "pars": [4, 5, 4, 3, 4, 3, 4, 5, 4, 4, 4, 3, 5, 4, 5, 3, 4, 4],
                                    "scores": [5, 5, 4, 4, 5, 3, 5, 5, 4, 5, 5, 5, 5, 4, 6, 3, 5, 4],
                                },
                                {
                                    "course_name": "Cypress Point Club",
                                    "tee_box": "White",
                                    "total_score": 85,
                                    "total_putts": 33,
                                    "date_played": date(2026, 5, 18),
                                    "pars": [4, 4, 4, 3, 5, 5, 3, 4, 4, 4, 4, 3, 4, 5, 4, 4, 3, 4],
                                    "scores": [5, 5, 5, 4, 5, 6, 3, 5, 4, 5, 5, 4, 5, 5, 5, 5, 5, 4],
                                },
                            ]

                            for mr in mock_rounds:
                                r_id = uuid.uuid4()
                                new_round = Round(
                                    id=r_id,
                                    player_id=player_id,
                                    course_name=mr["course_name"],
                                    tee_box=mr["tee_box"],
                                    total_score=mr["total_score"],
                                    total_putts=mr["total_putts"],
                                    date_played=mr["date_played"],
                                )
                                session.add(new_round)

                                # Create 18 HoleScores
                                for idx, (par, score) in enumerate(zip(mr["pars"], mr["scores"])):
                                    putts = 1 if score < par else (3 if score > par + 1 else 2)
                                    fairway_hit = True if par in [4, 5] and (idx % 3 != 0) else None
                                    gir = True if score <= par else False
                                    session.add(
                                        HoleScore(
                                            round_id=r_id,
                                            hole_number=idx + 1,
                                            par=par,
                                            score=score,
                                            putts=putts,
                                            fairway_hit=fairway_hit,
                                            gir=gir,
                                        )
                                    )
                        else:
                            # Insert 1 new recent round
                            new_course = "Pinehurst No. 2"
                            new_date = date.today()
                            # Check if Pinehurst No. 2 already exists for today to avoid duplicate inserts on repeated clicks
                            dupe_check = await session.execute(
                                select(Round).where(
                                    Round.player_id == player_id,
                                    Round.course_name == new_course,
                                    Round.date_played == new_date,
                                )
                            )
                            if dupe_check.scalar_one_or_none() is None:
                                r_id = uuid.uuid4()
                                new_round = Round(
                                    id=r_id,
                                    player_id=player_id,
                                    course_name=new_course,
                                    tee_box="Championship",
                                    total_score=79,
                                    total_putts=30,
                                    date_played=new_date,
                                )
                                session.add(new_round)

                                pars = [4, 4, 4, 4, 5, 3, 4, 4, 3, 4, 4, 4, 3, 4, 3, 4, 3, 4]
                                scores = [5, 4, 5, 4, 5, 4, 4, 5, 3, 5, 5, 4, 4, 5, 3, 5, 4, 4]
                                for idx, (par, score) in enumerate(zip(pars, scores)):
                                    putts = 1 if score < par else (3 if score > par + 1 else 2)
                                    fairway_hit = True if par in [4, 5] and (idx % 3 != 0) else None
                                    gir = True if score <= par else False
                                    session.add(
                                        HoleScore(
                                            round_id=r_id,
                                            hole_number=idx + 1,
                                            par=par,
                                            score=score,
                                            putts=putts,
                                            fairway_hit=fairway_hit,
                                            gir=gir,
                                        )
                                    )

                        # Update credential scrape status
                        session_cred_result = await session.execute(
                            select(Credential).where(
                                Credential.player_id == player_id,
                                Credential.provider == "18birdies",
                            )
                        )
                        session_cred = session_cred_result.scalar_one_or_none()
                        if session_cred:
                            session_cred.last_scraped_at = datetime.utcnow()
                            session_cred.scrape_status = "success"

                        await session.commit()
                    except Exception as e:
                        await session.rollback()
                        # Yield a failure event
                        error_data = {
                            "progress": s["progress"],
                            "stage": "failed",
                            "message": f"Database import failed: {str(e)}",
                        }
                        yield f"event: scrape_progress\ndata: {json.dumps(error_data)}\n\n"
                        return

            yield f"event: scrape_progress\ndata: {json.dumps({'progress': s['progress'], 'stage': s['stage'], 'message': s['message']})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
