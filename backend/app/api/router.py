"""
Central API router for the SmartFit backend.

This module provides a single root APIRouter that is used
to register all SmartFit API route modules.

Individual route modules are kept inside app.api.routes
while this module provides the central registration point.
"""

from fastapi import APIRouter

from app.api.routes import (
    avatars,
    garments,
    users,
    videos,
    virtual_fittings,
)


# ============================================================
# Central API Router
# ============================================================

# All SmartFit API endpoints are grouped under /api.
api_router = APIRouter(
    prefix="/api",
)


# ============================================================
# User Routes
# ============================================================

api_router.include_router(
    users.router,
)


# ============================================================
# Video Routes
# ============================================================

api_router.include_router(
    videos.router,
)


# ============================================================
# Avatar Routes
# ============================================================

api_router.include_router(
    avatars.router,
)


# ============================================================
# Garment Routes
# ============================================================

api_router.include_router(
    garments.router,
)


# ============================================================
# Virtual Fitting Routes
# ============================================================

api_router.include_router(
    virtual_fittings.router,
)