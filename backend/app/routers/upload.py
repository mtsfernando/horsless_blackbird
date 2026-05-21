"""Upload endpoints — file upload and import history."""

import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.raw_import import RawImport
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def upload_file(
    file: UploadFile = File(...),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Upload a data file for import — placeholder.

    Args:
        file: The uploaded file.
        _current_user: The authenticated user.

    Returns:
        A 501 status with a message.
    """
    return {
        "detail": "File upload processing not yet implemented",
        "filename": file.filename,
    }


@router.get("/history")
async def get_upload_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get the import history for the current user.

    Args:
        db: The async database session.
        current_user: The authenticated user.

    Returns:
        A list of raw import records.
    """
    result = await db.execute(
        select(RawImport)
        .where(RawImport.user_id == current_user.id)
        .order_by(RawImport.imported_at.desc())
    )
    imports = result.scalars().all()

    return [
        {
            "id": imp.id,
            "source": imp.source,
            "filename": imp.filename,
            "status": imp.status,
            "imported_at": imp.imported_at.isoformat(),
        }
        for imp in imports
    ]


@router.post("/raw", status_code=status.HTTP_201_CREATED)
async def upload_raw_json(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Upload a raw JSON payload directly to the database raw_imports table.

    Args:
        payload: The raw JSON data to import.
        current_user: The authenticated user.
        db: The async database session.

    Returns:
        A success message and the ID of the new raw import record.
    """
    raw_import = RawImport(
        user_id=current_user.id,
        source="scraper",
        filename="scraper_upload.json",
        raw_json=payload,
        status="pending",
    )
    db.add(raw_import)
    await db.commit()
    await db.refresh(raw_import)
    
    return {
        "status": "success",
        "message": "Raw data imported successfully",
        "import_id": str(raw_import.id),
    }
