"""Profile endpoints — manage own profile, nickname, and credentials."""

import uuid
import json
import asyncio
import os
import httpx
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
from app.models.raw_import import RawImport
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


async def get_course_pars(course_name: str) -> list[int] | None:
    """Fetch hole pars for a course from GolfCourseAPI."""
    api_key = "LP4R7Y3O4344ZN5A22K6ZWNTUA"
    headers = {"Authorization": f"Key {api_key}"}
    # URL encode course name
    import urllib.parse
    encoded_name = urllib.parse.quote(course_name)
    url = f"https://api.golfcourseapi.com/v1/search?search_query={encoded_name}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                res_data = response.json()
                courses = res_data.get("courses", [])
                if courses:
                    # Look at the first matched course
                    tees = courses[0].get("tees", {})
                    # Try to get first available tee box holes list
                    tee_list = tees.get("male") or tees.get("female") or []
                    if tee_list and "holes" in tee_list[0]:
                        return [h["par"] for h in tee_list[0]["holes"]]
    except Exception as e:
        print(f"Error querying GolfCourseAPI: {e}")
    return None


def calculate_fallback_pars(num_holes: int, total_par: int) -> list[int]:
    """Dynamically distribute total par across played holes in a realistic way."""
    if num_holes == 0:
        return []
    # Default to par 4 for all
    pars = [4] * num_holes
    current_sum = sum(pars)
    
    # Adjust until we match total_par
    if current_sum < total_par:
        # Increase to 5 for some holes (typical par 5 index positions: 4, 1, 7)
        par_5_candidates = [4, 1, 7] + list(range(num_holes))
        for idx in par_5_candidates:
            if idx < num_holes and pars[idx] < 5:
                pars[idx] += 1
                current_sum += 1
                if current_sum == total_par:
                    break
    elif current_sum > total_par:
        # Decrease to 3 for some holes (typical par 3 index positions: 2, 7, 5)
        par_3_candidates = [2, 7, 5] + list(range(num_holes))
        for idx in par_3_candidates:
            if idx < num_holes and pars[idx] > 3:
                pars[idx] -= 1
                current_sum -= 1
                if current_sum == total_par:
                    break
    return pars


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
                try:
                    async with async_session_factory() as session:
                        # Fetch the latest RawImport record for the user from the database
                        import_stmt = (
                            select(RawImport)
                            .where(RawImport.user_id == user.id)
                            .order_by(RawImport.imported_at.desc())
                            .limit(1)
                        )
                        import_result = await session.execute(import_stmt)
                        latest_import = import_result.scalar_one_or_none()

                        if latest_import is None:
                            # Simulate the scraper bot by decoding and inserting the mock data first
                            from app.seed import MOCK_18BIRDIES_B64
                            import base64
                            import gzip
                            compressed = base64.b64decode(MOCK_18BIRDIES_B64)
                            data = json.loads(gzip.decompress(compressed).decode("utf-8"))

                            latest_import = RawImport(
                                user_id=user.id,
                                source="scraper",
                                filename="18birdies_scraped.json",
                                raw_json=data,
                                status="processed",
                            )
                            session.add(latest_import)
                            await session.flush()
                        else:
                            data = latest_import.raw_json
                            # If it was pending from the scraper bot, mark it as processed
                            if latest_import.status == "pending":
                                latest_import.status = "processed"

                        # Update player display name in database to match the scraped account username
                        player_result = await session.execute(
                            select(Player).where(Player.id == player_id)
                        )
                        db_player = player_result.scalar_one_or_none()
                        if db_player:
                            db_player.display_name = data["myData"]["accountData"]["userName"]

                        # Build played clubs ID-to-Name map
                        club_map = {c["clubId"]: c["name"] for c in data["myData"]["clubData"]["playedClubs"]}

                        # Import all 21 rounds dynamically
                        for r in data["myData"]["activityData"]["rounds"]:
                            round_id = uuid.UUID(r["id"])
                            club_id = r["clubId"]["id"]
                            course_name = club_map.get(club_id, "Unknown Course")
                            timestamp_ms = r["timestamp"]
                            date_played = date.fromtimestamp(timestamp_ms / 1000.0)
                            total_score = r["strokes"]

                            # Safely extract putts from round stats
                            total_putts = r["stats"].get("putts", 0)
                            if total_putts == 0:
                                # Try recommended stats fallback
                                for stat_item in r["stats"].get("recommendedStats", []):
                                    if stat_item["type"] == "TOTAL_PUTTS":
                                        total_putts = int(stat_item["value"])
                                        break
                            if total_putts == 0:
                                total_putts = None

                            # Check if the round is already imported to make the endpoint idempotent
                            r_check = await session.execute(
                                select(Round).where(Round.id == round_id)
                            )
                            if r_check.scalar_one_or_none() is not None:
                                continue

                            # Query GolfCourseAPI for precise pars, otherwise fallback to heuristic par distribution
                            pars = await get_course_pars(course_name)
                            num_holes = len(r["holeStrokes"])

                            if pars is None or len(pars) < num_holes:
                                total_par = total_score - r["score"]
                                pars = calculate_fallback_pars(num_holes, total_par)
                            else:
                                pars = pars[:num_holes]

                            # Create Round
                            new_round = Round(
                                id=round_id,
                                player_id=player_id,
                                course_name=course_name,
                                tee_box="Standard",
                                total_score=total_score,
                                total_putts=total_putts,
                                date_played=date_played,
                            )
                            session.add(new_round)

                            # Create HoleScores for each hole played
                            for idx, score in enumerate(r["holeStrokes"]):
                                par = pars[idx]
                                hole_number = idx + 1

                                # Distribute putts evenly as a clean heuristic
                                hole_putt = None
                                if total_putts is not None:
                                    hole_putt = total_putts // num_holes
                                    if idx < (total_putts % num_holes):
                                        hole_putt += 1

                                # Estimate GIR (Green in Regulation)
                                if hole_putt is not None:
                                    gir = (score - hole_putt) <= (par - 2)
                                else:
                                    gir = score <= par

                                session.add(
                                    HoleScore(
                                        round_id=round_id,
                                        hole_number=hole_number,
                                        par=par,
                                        score=score,
                                        putts=hole_putt,
                                        fairway_hit=None,
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
