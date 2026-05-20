"""Admin credential management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.credential import CredentialCreate, CredentialResponse, CredentialUpdate
from app.services import credential_service
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.post(
    "",
    response_model=CredentialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credential(
    payload: CredentialCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> CredentialResponse:
    """Store a new encrypted credential for a player.

    Args:
        payload: The credential data (player_id, provider, username, password).
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        The created credential metadata (no passwords).
    """
    cred = await credential_service.store_credential(
        db, payload.player_id, payload.provider, payload.username, payload.password
    )
    return CredentialResponse.model_validate(cred)


@router.get("", response_model=list[CredentialResponse])
async def list_credentials(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[CredentialResponse]:
    """List all credentials (metadata only, no passwords).

    Args:
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        A list of all credential metadata.
    """
    creds = await credential_service.list_credentials(db)
    return [CredentialResponse.model_validate(c) for c in creds]


@router.put("/{cred_id}", response_model=CredentialResponse)
async def update_credential(
    cred_id: uuid.UUID,
    payload: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> CredentialResponse:
    """Update an existing credential's username and/or password.

    Args:
        cred_id: The credential's UUID.
        payload: The fields to update.
        db: The async database session.
        _current_user: The authenticated user (for access control).

    Returns:
        The updated credential metadata (no passwords).
    """
    cred = await credential_service.update_credential(
        db, cred_id, payload.username, payload.password
    )
    if cred is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )
    return CredentialResponse.model_validate(cred)


@router.delete("/{cred_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    cred_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> None:
    """Delete a credential by ID.

    Args:
        cred_id: The credential's UUID.
        db: The async database session.
        _current_user: The authenticated user (for access control).
    """
    deleted = await credential_service.delete_credential(db, cred_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found",
        )


@router.post("/{cred_id}/test", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def test_credential(
    cred_id: uuid.UUID,
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Test a credential against the provider — placeholder.

    Args:
        cred_id: The credential's UUID.
        _current_user: The authenticated user (for access control).

    Returns:
        A 501 status with a message.
    """
    return {"detail": "Credential testing not yet implemented"}
