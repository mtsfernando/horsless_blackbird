"""Seeding script to create internal users and administrator."""

import os
import asyncio
import base64
import gzip
import json
import uuid
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_factory
from app.services import auth_service
from app.models.round import Round
from app.models.hole_score import HoleScore
from app.models.raw_import import RawImport
from app.models.player import Player
from app.routers.profile import calculate_fallback_pars

# Compact gzipped, base64-encoded mock 18Birdies data containing 21 rounds
MOCK_18BIRDIES_B64 = (
    "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"
)


async def seed_18birdies_data(db: AsyncSession, user) -> None:
    """Helper to seed the 18Birdies mock data for a user."""
    # Decode gzipped mock data
    compressed = base64.b64decode(MOCK_18BIRDIES_B64)
    raw_json = json.loads(gzip.decompress(compressed).decode("utf-8"))

    # Update player display name to match scraped username
    if user.player:
        user.player.display_name = raw_json["myData"]["accountData"]["userName"]
    
    # Store in raw_imports if it doesn't exist
    import_stmt = select(RawImport).where(
        RawImport.user_id == user.id,
        RawImport.source == "scraper",
    )
    import_result = await db.execute(import_stmt)
    existing_import = import_result.scalar_one_or_none()

    if not existing_import:
        print(f"Creating seeded RawImport for {user.email}...")
        raw_import = RawImport(
            user_id=user.id,
            source="scraper",
            filename="18birdies_scraped.json",
            raw_json=raw_json,
            status="processed",
        )
        db.add(raw_import)
        await db.flush()

    # Map clubs
    club_map = {c["clubId"]: c["name"] for c in raw_json["myData"]["clubData"]["playedClubs"]}

    # Import 21 rounds
    player_id = user.player.id
    for r in raw_json["myData"]["activityData"]["rounds"]:
        round_id = uuid.UUID(r["id"])
        club_id = r["clubId"]["id"]
        course_name = club_map.get(club_id, "Unknown Course")
        timestamp_ms = r["timestamp"]
        date_played = date.fromtimestamp(timestamp_ms / 1000.0)
        total_score = r["strokes"]

        # Extract total putts
        total_putts = r["stats"].get("putts", 0)
        if total_putts == 0:
            for stat_item in r["stats"].get("recommendedStats", []):
                if stat_item["type"] == "TOTAL_PUTTS":
                    total_putts = int(stat_item["value"])
                    break
        if total_putts == 0:
            total_putts = None

        # Check for existing round
        r_check = await db.execute(select(Round).where(Round.id == round_id))
        if r_check.scalar_one_or_none() is not None:
            continue

        num_holes = len(r["holeStrokes"])
        total_par = total_score - r["score"]
        pars = calculate_fallback_pars(num_holes, total_par)

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
        db.add(new_round)

        # Create HoleScores
        for idx, score in enumerate(r["holeStrokes"]):
            par = pars[idx]
            hole_number = idx + 1

            # Putts heuristic
            hole_putt = None
            if total_putts is not None:
                hole_putt = total_putts // num_holes
                if idx < (total_putts % num_holes):
                    hole_putt += 1

            # GIR heuristic
            if hole_putt is not None:
                gir = (score - hole_putt) <= (par - 2)
            else:
                gir = score <= par

            db.add(
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
    print(f"Successfully seeded 18Birdies rounds & scores for {user.email}")


async def seed_data() -> None:
    """Seed initial user accounts and player profiles."""
    async with async_session_factory() as db:
        users_to_seed = [
            {
                "email": "thilina.fernando9@gmail.com",
                "password": os.getenv("ADMIN_SEED_PASSWORD", "mtsf1234"),
                "display_name": "Thilina Fernando",
                "is_admin": True,
            },
            {
                "email": "sathira2000@gmail.com",
                "password": os.getenv("RANSIKA_SEED_PASSWORD", "RansikaPlayer2026!"),
                "display_name": "Ransika Bellanage",
                "is_admin": False,
            },
            {
                "email": "aqeel.miskin@gmail.com",
                "password": os.getenv("AQEEL_SEED_PASSWORD", "AqeelPlayer2026!"),
                "display_name": "Aqeel Miskin",
                "is_admin": False,
            },
        ]

        for u in users_to_seed:
            existing = await auth_service.get_user_by_email(db, u["email"])
            if existing is None:
                print(f"Seeding user {u['email']}...")
                user = await auth_service.register_user(
                    db,
                    email=u["email"],
                    password=u["password"],
                    display_name=u["display_name"],
                    is_admin=u["is_admin"],
                )
            else:
                print(
                    f"User {u['email']} already exists. Ensuring is_admin is {u['is_admin']} and password is set..."
                )
                existing.is_admin = u["is_admin"]
                existing.password_hash = auth_service.hash_password(u["password"])
                user = existing
                if not existing.player:
                    print(
                        f"Creating missing player profile for {u['email']}..."
                    )
                    player = Player(
                        user_id=existing.id,
                        display_name=u["display_name"],
                    )
                    db.add(player)
                else:
                    existing.player.display_name = u["display_name"]

            # Automatically seed 18Birdies raw imports and rounds for the primary admin user
            if u["email"] == "thilina.fernando9@gmail.com":
                # Ensure the player object is flushed and associated
                await db.flush()
                await seed_18birdies_data(db, user)

        await db.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
