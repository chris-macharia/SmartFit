"""
Virtual fitting API routes for SmartFit.

This module provides HTTP endpoints for:

1. Creating a virtual fitting.
2. Retrieving a virtual fitting by ID.

Virtual fitting operations require authentication.

A customer can only use their own generated avatar, while
garments may belong to retailers or other users.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.virtual_fitting import (
    VirtualFittingCreate,
    VirtualFittingResponse,
)
from app.services.virtual_fitting_service import (
    create_virtual_fitting,
    get_virtual_fitting_by_id,
)


# ============================================================
# Router Configuration
# ============================================================

router = APIRouter(
    prefix="/virtual-fittings",
    tags=["Virtual Fittings"],
)


# ============================================================
# CREATE VIRTUAL FITTING
# ============================================================


@router.post(
    "/",
    response_model=VirtualFittingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_virtual_fitting_endpoint(
    fitting_data: VirtualFittingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a virtual fitting for the authenticated user.

    The fitting combines:

    - The user's generated avatar.
    - A selected garment.
    - The user's body measurements associated with the avatar.

    Args:
        fitting_data:
            Request containing the avatar ID and garment ID.

        db:
            Active SQLAlchemy database session.

        current_user:
            Authenticated SmartFit user.

    Returns:
        VirtualFittingResponse:
            The newly created virtual fitting.

    Raises:
        HTTPException 404:
            If the avatar, body measurement, measurement video,
            or garment cannot be found.

        HTTPException 409:
            If the same avatar and garment have already been used
            by the authenticated user.

        HTTPException 400:
            If the fitting cannot be created because of another
            business validation error.
    """

    try:
        # --------------------------------------------------------
        # Create the virtual fitting.
        # --------------------------------------------------------

        fitting = create_virtual_fitting(
            db=db,
            user_id=current_user.user_id,
            avatar_id=fitting_data.avatar_id,
            garment_id=fitting_data.garment_id,
        )

        return fitting

    except ValueError as exc:
        # --------------------------------------------------------
        # Map service-layer errors to appropriate HTTP responses.
        # --------------------------------------------------------
        #
        # The service uses ValueError for business-level failures.
        # The API converts those errors into meaningful HTTP status
        # codes for the frontend.

        error_message = str(exc)

        # --------------------------------------------------------
        # Resource-not-found errors.
        # --------------------------------------------------------

        if error_message in {
            "Avatar not found.",
            "Body measurement not found.",
            "Body measurement video not found.",
            "Garment not found.",
        }:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            ) from exc

        # --------------------------------------------------------
        # Duplicate fitting.
        # --------------------------------------------------------

        if error_message == (
            "A virtual fitting already exists "
            "for this avatar and garment."
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message,
            ) from exc

        # --------------------------------------------------------
        # Other business validation errors.
        # --------------------------------------------------------

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        ) from exc


# ============================================================
# GET VIRTUAL FITTING
# ============================================================


@router.get(
    "/{fitting_id}",
    response_model=VirtualFittingResponse,
    status_code=status.HTTP_200_OK,
)
def get_virtual_fitting_endpoint(
    fitting_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a virtual fitting belonging to the authenticated user.

    Args:
        fitting_id:
            UUID of the virtual fitting.

        db:
            Active SQLAlchemy database session.

        current_user:
            Authenticated SmartFit user.

    Returns:
        VirtualFittingResponse:
            The requested virtual fitting.

    Raises:
        HTTPException 404:
            If the virtual fitting does not exist or does not belong
            to the authenticated user.
    """

    fitting = get_virtual_fitting_by_id(
        db=db,
        fitting_id=fitting_id,
        user_id=current_user.user_id,
    )

    if fitting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual fitting not found.",
        )

    return fitting
