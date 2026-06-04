"""Authentication endpoints — register, login, and current user."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
) -> dict:
    """Handle forgot password requests.

    Generates a password reset token if the email exists.
    """
    user = await auth_service.get_user_by_email(db, payload.email)
    if user is None:
        # Avoid user enumeration attacks in production, but let's return success message.
        return {
            "message": "If the email address exists in our system, a password reset link has been sent.",
            "dev_token": None,
        }

    # Generate a short-lived token (15 mins) specifically for resetting password.
    token = create_access_token(
        data={"sub": str(user.id), "type": "reset"},
        expires_delta=timedelta(minutes=15),
    )

    return {
        "message": "If the email address exists in our system, a password reset link has been sent.",
        "dev_token": token,
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

