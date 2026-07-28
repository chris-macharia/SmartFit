"""
Central API router for the SmartFit backend.

This module provides a single root APIRouter that is used
to register all SmartFit API route modules.

As the project grows, individual route modules such as users,
garments, videos, avatars, and virtual fittings will be included
through this central router.
"""

from fastapi import APIRouter

from app.api.routes import users

# Create the central API router.
#
# Individual route modules are included below.
# This keeps app/main.py clean and provides a single location
# for managing the application's API routes.
api_router = APIRouter(
    prefix="/api"
)


# Register the User API routes.
#
# This makes the user endpoints available under:
#
#     /api/users
#
# For example:
#
#     POST /api/users/
#
api_router.include_router(
    users.router
)