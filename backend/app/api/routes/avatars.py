"""
Avatar API routes for SmartFit.

This module provides endpoints for generating and retrieving
personalized SmartFit avatars.

Avatar generation is a separate operation from video processing.
A completed body measurement is used as the input to generate
the avatar.
"""

import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.avatar import AvatarResponse
from app.services.avatar_generator import (
    AvatarGenerationError,
)
from app.services.avatar_service import (
    create_avatar,
    get_avatar_by_id,
)


# ============================================================
# Router Configuration
# ============================================================

router = APIRouter(
    prefix="/avatars",
    tags=["Avatars"],
)


# ============================================================
# CREATE - Generate Avatar
# ============================================================

@router.post(
    "/",
    response_model=AvatarResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_avatar(
    measurement_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an avatar from an existing body measurement.

    The body measurement must belong to a video owned by the
    authenticated user.

    Avatar generation is intentionally separate from video
    processing so that the two stages can evolve independently.
    """

    try:
        return create_avatar(
            db=db,
            measurement_id=measurement_id,
            user_id=current_user.user_id,
        )

    except ValueError as exc:
        detail = str(exc)

        if detail == "Body measurement not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            ) from exc

        if (
            detail
            == "An avatar already exists for this body measurement."
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc

    except AvatarGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


# ============================================================
# READ - Retrieve Avatar
# ============================================================

@router.get(
    "/{avatar_id}",
    response_model=AvatarResponse,
    status_code=status.HTTP_200_OK,
)
def get_avatar(
    avatar_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve an avatar belonging to the authenticated user.
    """

    avatar = get_avatar_by_id(
        db=db,
        avatar_id=avatar_id,
        user_id=current_user.user_id,
    )

    if avatar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found.",
        )

    return avatar