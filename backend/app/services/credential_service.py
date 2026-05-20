"""Credential service — CRUD operations for encrypted provider credentials."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credential import Credential
from app.utils.encryption import encrypt, decrypt


async def store_credential(
    db: AsyncSession,
    player_id: uuid.UUID,
    provider: str,
    username: str,
    password: str,
) -> Credential:
    """Store a new encrypted credential for a player.

    Args:
        db: The async database session.
        player_id: The player's UUID.
        provider: The provider name (e.g. '18birdies').
        username: The plaintext username to encrypt and store.
        password: The plaintext password to encrypt and store.

    Returns:
        The newly created Credential instance.
    """
    credential = Credential(
        player_id=player_id,
        provider=provider,
        username_enc=encrypt(username),
        password_enc=encrypt(password),
    )
    db.add(credential)
    await db.flush()
    await db.refresh(credential)
    return credential


async def get_credential_decrypted(
    db: AsyncSession,
    player_id: uuid.UUID,
    provider: str = "18birdies",
) -> dict | None:
    """Retrieve and decrypt a credential for a player and provider.

    Args:
        db: The async database session.
        player_id: The player's UUID.
        provider: The provider name to look up.

    Returns:
        A dict with 'username' and 'password' in plaintext, or None if
        no credential is found.
    """
    result = await db.execute(
        select(Credential).where(
            Credential.player_id == player_id,
            Credential.provider == provider,
        )
    )
    cred = result.scalar_one_or_none()
    if cred is None:
        return None
    return {
        "id": cred.id,
        "username": decrypt(cred.username_enc),
        "password": decrypt(cred.password_enc),
    }


async def update_credential(
    db: AsyncSession,
    cred_id: uuid.UUID,
    username: str | None = None,
    password: str | None = None,
) -> Credential | None:
    """Update an existing credential's encrypted username and/or password.

    Args:
        db: The async database session.
        cred_id: The credential's UUID.
        username: New plaintext username (optional).
        password: New plaintext password (optional).

    Returns:
        The updated Credential instance, or None if not found.
    """
    result = await db.execute(select(Credential).where(Credential.id == cred_id))
    cred = result.scalar_one_or_none()
    if cred is None:
        return None

    if username is not None:
        cred.username_enc = encrypt(username)
    if password is not None:
        cred.password_enc = encrypt(password)

    await db.flush()
    await db.refresh(cred)
    return cred


async def delete_credential(db: AsyncSession, cred_id: uuid.UUID) -> bool:
    """Delete a credential by ID.

    Args:
        db: The async database session.
        cred_id: The credential's UUID.

    Returns:
        True if the credential was deleted, False if not found.
    """
    result = await db.execute(select(Credential).where(Credential.id == cred_id))
    cred = result.scalar_one_or_none()
    if cred is None:
        return False

    await db.delete(cred)
    await db.flush()
    return True


async def list_credentials(db: AsyncSession) -> list[Credential]:
    """List all credentials (metadata only — no decrypted passwords).

    Args:
        db: The async database session.

    Returns:
        A list of Credential ORM instances.
    """
    result = await db.execute(select(Credential))
    return list(result.scalars().all())
