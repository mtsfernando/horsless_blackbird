"""Horseless Blackbird API — FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, profile, players, rounds, leaderboard, credentials, upload, email, activity

logger = logging.getLogger("horseless_blackbird")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — runs on startup and shutdown."""
    logger.info("Horseless Blackbird API started")
    yield
    logger.info("Horseless Blackbird API shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application instance.
    """
    application = FastAPI(
        title="Horseless Blackbird",
        description="Golf dashboard API for tracking rounds, scores, and leaderboards.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include all routers under /api
    application.include_router(auth.router, prefix="/api")
    application.include_router(profile.router, prefix="/api")
    application.include_router(players.router, prefix="/api")
    application.include_router(rounds.router, prefix="/api")
    application.include_router(leaderboard.router, prefix="/api")
    application.include_router(credentials.router, prefix="/api")
    application.include_router(upload.router, prefix="/api")
    application.include_router(email.router, prefix="/api")
    application.include_router(activity.router, prefix="/api")

    @application.get("/api/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint.

        Returns:
            A simple status dict.
        """
        return {"status": "healthy", "service": "horseless-blackbird"}

    return application


app = create_app()
