"""Authentication service — user registration and login logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.player import Player
from app.utils.security import hash_password, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Look up a user by email address.

    Args:
        db: The async database session.
        email: The email address to search for.

    Returns:
        The User if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    display_name: str | None = None,
    is_admin: bool = False,
) -> User:
    """Register a new user account.

    Args:
        db: The async database session.
        email: The user's email address.
        password: The plaintext password (will be hashed before storing).
        display_name: Optional display name for the linked Player profile.
        is_admin: Whether this user has admin status.

    Returns:
        The newly created User instance.

    Raises:
        ValueError: If a user with this email already exists.
    """
    existing = await get_user_by_email(db, email)
    if existing is not None:
        raise ValueError("A user with this email already exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
        is_admin=is_admin,
    )
    db.add(user)
    await db.flush()

    # Automatically create associated Player profile to avoid 404s in frontend
    player = Player(
        user_id=user.id,
        display_name=display_name or email.split("@")[0],
    )
    db.add(player)
    await db.flush()

    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate a user by email and password.

    Args:
        db: The async database session.
        email: The user's email address.
        password: The plaintext password to verify.

    Returns:
        The User if credentials are valid, otherwise None.
    """
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
