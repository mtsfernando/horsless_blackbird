"""Authentication endpoints — register, login, and current user."""

from datetime import timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
import httpx
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services import auth_service
from app.utils.dependencies import get_current_user
from app.utils.security import create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Register a new user account.

    Args:
        payload: The user registration data (email, password, display_name).
        db: The async database session.

    Returns:
        The created user data.
    """
    try:
        user = await auth_service.register_user(
            db, payload.email, payload.password, payload.display_name
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    """Authenticate a user and return a JWT access token.

    Args:
        payload: The login credentials (email, password).
        db: The async database session.

    Returns:
        A JWT access token with the user profile information.
    """
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated user's profile.

    Args:
        current_user: The authenticated user (injected via dependency).

    Returns:
        The current user's data.
    """
    return current_user


logger = logging.getLogger("horseless_blackbird")


async def send_reset_email(email: str, token: str, base_url: str) -> bool:
    from app.config import settings

    if not settings.MAILGUN_API_KEY or not settings.MAILGUN_DOMAIN:
        logger.warning("Mailgun API key or domain not configured. Cannot send email.")
        return False

    url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
    auth = ("api", settings.MAILGUN_API_KEY)
    reset_link = f"{base_url}reset-password?token={token}"

    data = {
        "from": f"Horseless Blackbird Support <noreply@{settings.MAILGUN_DOMAIN}>",
        "to": email,
        "subject": "Reset Your Password - Horseless Blackbird",
        "text": f"Hello,\n\nYou requested to reset your password. Please click the link below to set a new password:\n\n{reset_link}\n\nThis link will expire in 15 minutes.\n\nIf you did not request this, please ignore this email.",
        "html": f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
          <h2 style="color: #10b981;">Horseless Blackbird</h2>
          <p>Hello,</p>
          <p>You requested to reset your password. Please click the button below to set a new password:</p>
          <div style="margin: 24px 0;">
            <a href="{reset_link}" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">Reset Password</a>
          </div>
          <p style="color: #64748b; font-size: 14px;">This link will expire in 15 minutes.</p>
          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
          <p style="color: #94a3b8; font-size: 12px;">If you did not request this, you can safely ignore this email.</p>
        </div>
        """,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, auth=auth, data=data, timeout=10.0)
            if response.status_code == 200:
                logger.info(f"Password reset email sent to {email}")
                return True
            else:
                logger.error(
                    f"Failed to send email via Mailgun: {response.status_code} - {response.text}"
                )
                return False
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> dict:
    """Handle forgot password requests.

    Generates a password reset token and sends an email if the email exists.
    """
    user = await auth_service.get_user_by_email(db, payload.email)
    if user is not None:
        # Generate a short-lived token (15 mins) specifically for resetting password.
        token = create_access_token(
            data={"sub": str(user.id), "type": "reset"},
            expires_delta=timedelta(minutes=15),
        )
        # Build base URL with header support for reverse proxies
        proto = request.headers.get("x-forwarded-proto", "http")
        host = (
            request.headers.get("x-forwarded-host")
            or request.headers.get("host")
            or str(request.base_url.netloc)
        )
        base_url = f"{proto}://{host}/"

        await send_reset_email(user.email, token, base_url)

    return {
        "message": "If the email address exists in our system, a password reset link has been sent."
    }



@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Handle password reset using a token."""
    try:
        token_payload = decode_access_token(payload.token)
        if token_payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )
        user_id = token_payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    success = await auth_service.reset_user_password(db, user_id, payload.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {"message": "Password has been reset successfully"}

