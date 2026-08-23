"""
Garment API routes for SmartFit.

This module provides endpoints for retailers to register,
retrieve, update, and delete garment measurements.

Garment operations are restricted to authenticated users
whose account role is "retailer".
"""

import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import require_retailer
from app.db.database import get_db
from app.models.user import User
from app.schemas.garment import (
    GarmentCreate,
    GarmentResponse,
    GarmentUpdate,
)
from app.services.garment_service import (
    create_garment,
    delete_garment,
    get_garment_by_id,
    get_garments_by_user,
    update_garment,
)


# ============================================================
# Router Configuration
# ============================================================

router = APIRouter(
    prefix="/garments",
    tags=["Garments"],
)


# ============================================================
# CREATE - Register Garment
# ============================================================

@router.post(
    "/",
    response_model=GarmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_garment(
    garment_data: GarmentCreate,
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """
    Register a new garment for the authenticated retailer.

    The retailer's user ID is obtained from the authenticated
    JWT rather than being supplied by the client.
    """

    return create_garment(
        db=db,
        user_id=current_user.user_id,
        chest_width=garment_data.chest_width,
        waist_width=garment_data.waist_width,
        hip_width=garment_data.hip_width,
        shoulder_width=garment_data.shoulder_width,
        inseam=garment_data.inseam,
    )


# ============================================================
# READ - Retrieve Retailer's Garments
# ============================================================

@router.get(
    "/",
    response_model=list[GarmentResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_garments(
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """
    Retrieve all garments registered by the authenticated retailer.
    """

    return get_garments_by_user(
        db=db,
        user_id=current_user.user_id,
    )


# ============================================================
# READ - Retrieve One Garment
# ============================================================

@router.get(
    "/{garment_id}",
    response_model=GarmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_garment(
    garment_id: uuid.UUID,
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific garment belonging to the authenticated
    retailer.
    """

    garment = get_garment_by_id(
        db=db,
        garment_id=garment_id,
        user_id=current_user.user_id,
    )

    if garment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garment not found.",
        )

    return garment


# ============================================================
# UPDATE - Update Garment
# ============================================================

@router.put(
    "/{garment_id}",
    response_model=GarmentResponse,
    status_code=status.HTTP_200_OK,
)
def edit_garment(
    garment_id: uuid.UUID,
    garment_data: GarmentUpdate,
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """
    Update the measurements of a garment belonging to the
    authenticated retailer.
    """

    garment = update_garment(
        db=db,
        garment_id=garment_id,
        user_id=current_user.user_id,
        chest_width=garment_data.chest_width,
        waist_width=garment_data.waist_width,
        hip_width=garment_data.hip_width,
        shoulder_width=garment_data.shoulder_width,
        inseam=garment_data.inseam,
    )

    if garment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garment not found.",
        )

    return garment


# ============================================================
# DELETE - Delete Garment
# ============================================================

@router.delete(
    "/{garment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_garment(
    garment_id: uuid.UUID,
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """
    Delete a garment belonging to the authenticated retailer.
    """

    deleted = delete_garment(
        db=db,
        garment_id=garment_id,
        user_id=current_user.user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Garment not found.",
        )

    return None