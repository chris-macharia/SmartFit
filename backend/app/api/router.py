"""
Central API router for the SmartFit backend.

This module provides a single root APIRouter that will be used
to register all SmartFit API route modules.

As the project grows, individual route modules such as users,
garments, videos, avatars, and virtual fittings will be included
through this central router.
"""

from fastapi import APIRouter


# Create the central API router.
#
# Individual route modules will eventually be included here.
# This keeps app/main.py clean and provides a single location
# for managing the application's API routes.
api_router = APIRouter(
    prefix="/api"
)