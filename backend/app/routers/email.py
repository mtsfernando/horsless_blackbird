"""Email endpoints — report sending and preview (placeholders)."""

from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send-report", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def send_report(
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Send an email report — placeholder.

    Args:
        _current_user: The authenticated user.

    Returns:
        A 501 status with a message.
    """
    return {"detail": "Email report sending not yet implemented"}


@router.get("/preview", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def preview_report(
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Preview an email report — placeholder.

    Args:
        _current_user: The authenticated user.

    Returns:
        A 501 status with a message.
    """
    return {"detail": "Email report preview not yet implemented"}
