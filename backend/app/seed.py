"""Seeding script to create internal users and administrator."""

import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_factory
from app.services import auth_service


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
                await auth_service.register_user(
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
                if not existing.player:
                    print(
                        f"Creating missing player profile for {u['email']}..."
                    )
                    from app.models.player import Player

                    player = Player(
                        user_id=existing.id,
                        display_name=u["display_name"],
                    )
                    db.add(player)
                else:
                    existing.player.display_name = u["display_name"]

        await db.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
