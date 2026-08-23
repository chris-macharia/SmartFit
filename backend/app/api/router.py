"""
Central API router for the SmartFit backend.

This module provides a single root APIRouter that is used
to register all SmartFit API route modules.

As the project grows, individual route modules such as users,
garments, videos, avatars, and virtual fittings will be included
through this central router.
"""

from fastapi import APIRouter

from app.api.routes import avatars, garments, users, videos


# Create the central API router.
api_router = APIRouter(
    prefix="/api"
)


# ============================================================
# User Routes
# ============================================================

api_router.include_router(
    users.router
)


# ============================================================
# Video Routes
# ============================================================

api_router.include_router(
    videos.router
)


# ============================================================
# Avatar Routes
# ============================================================

api_router.include_router(
    avatars.router
)


# ============================================================
# Garment Routes
# ============================================================

api_router.include_router(
    garments.router
)