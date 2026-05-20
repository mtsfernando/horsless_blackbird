"""Authentication endpoints — register, login, and current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services import auth_service
from app.utils.dependencies import get_current_user
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Register a new user account.

    Args:
        payload: The user registration data (email, password).
        db: The async database session.

    Returns:
        The created user data.
    """
    try:
        user = await auth_service.register_user(db, payload.email, payload.password)
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
        A JWT access token.
    """
    user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Get the currently authenticated user's profile.

    Args:
        current_user: The authenticated user (injected via dependency).

    Returns:
        The current user's data.
    """
    return current_user
