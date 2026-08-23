"""
Garment service for SmartFit.

This module contains the database and application logic used by
the garment API.

Garments are uploaded and managed by authenticated retailer
accounts. The service receives the authenticated user's UUID
from the API layer and uses it to establish garment ownership.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.garment import Garment


# ============================================================
# Create Garment
# ============================================================

def create_garment(
    db: Session,
    user_id: uuid.UUID,
    chest_width: float,
    waist_width: float,
    hip_width: float,
    shoulder_width: float,
    inseam: float,
) -> Garment:
    """
    Create and persist a new garment.

    The user_id must belong to the authenticated retailer.
    Authorization that the user is actually a retailer is handled
    by the API dependency layer.

    Args:
        db:
            Active SQLAlchemy database session.

        user_id:
            UUID of the authenticated retailer uploading the garment.

        chest_width:
            Garment chest width in centimetres.

        waist_width:
            Garment waist width in centimetres.

        hip_width:
            Garment hip width in centimetres.

        shoulder_width:
            Garment shoulder width in centimetres.

        inseam:
            Garment inseam length in centimetres.

    Returns:
        Garment:
            The newly created garment.
    """

    # --------------------------------------------------------
    # Create Garment
    # --------------------------------------------------------

    garment = Garment(
        garment_id=uuid.uuid4(),
        user_id=user_id,
        chest_width=chest_width,
        waist_width=waist_width,
        hip_width=hip_width,
        shoulder_width=shoulder_width,
        inseam=inseam,
    )

    # --------------------------------------------------------
    # Save Database Record
    # --------------------------------------------------------

    try:
        db.add(garment)
        db.commit()
        db.refresh(garment)

    except Exception as exc:
        db.rollback()

        raise RuntimeError(
            "Unable to create the garment record."
        ) from exc

    return garment


# ============================================================
# Retrieve Garment
# ============================================================

def get_garment_by_id(
    db: Session,
    garment_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Garment | None:
    """
    Retrieve a garment by ID if it belongs to the authenticated user.

    Args:
        db:
            Active SQLAlchemy database session.

        garment_id:
            UUID of the requested garment.

        user_id:
            UUID of the authenticated retailer.

    Returns:
        Garment:
            The garment if it exists and belongs to the user.

        None:
            If the garment does not exist or does not belong
            to the authenticated user.
    """

    return (
        db.query(Garment)
        .filter(
            Garment.garment_id == garment_id,
            Garment.user_id == user_id,
        )
        .first()
    )


# ============================================================
# Retrieve User Garments
# ============================================================

def get_garments_by_user(
    db: Session,
    user_id: uuid.UUID,
) -> list[Garment]:
    """
    Retrieve all garments uploaded by a specific user.

    Args:
        db:
            Active SQLAlchemy database session.

        user_id:
            UUID of the authenticated retailer.

    Returns:
        list[Garment]:
            All garments belonging to the user.
    """

    return (
        db.query(Garment)
        .filter(
            Garment.user_id == user_id,
        )
        .order_by(
            Garment.created_at.desc(),
        )
        .all()
    )


# ============================================================
# Update Garment
# ============================================================

def update_garment(
    db: Session,
    garment_id: uuid.UUID,
    user_id: uuid.UUID,
    chest_width: float | None = None,
    waist_width: float | None = None,
    hip_width: float | None = None,
    shoulder_width: float | None = None,
    inseam: float | None = None,
) -> Garment | None:
    """
    Update an existing garment owned by the authenticated user.

    Only values explicitly provided are updated.

    Args:
        db:
            Active SQLAlchemy database session.

        garment_id:
            UUID of the garment to update.

        user_id:
            UUID of the authenticated retailer.

        chest_width:
            New chest width, if provided.

        waist_width:
            New waist width, if provided.

        hip_width:
            New hip width, if provided.

        shoulder_width:
            New shoulder width, if provided.

        inseam:
            New inseam, if provided.

    Returns:
        Garment:
            The updated garment.

        None:
            If the garment does not exist or does not belong
            to the authenticated user.
    """

    # --------------------------------------------------------
    # Find Garment and Verify Ownership
    # --------------------------------------------------------

    garment = (
        db.query(Garment)
        .filter(
            Garment.garment_id == garment_id,
            Garment.user_id == user_id,
        )
        .first()
    )

    if garment is None:
        return None

    # --------------------------------------------------------
    # Update Provided Fields
    # --------------------------------------------------------

    if chest_width is not None:
        garment.chest_width = chest_width

    if waist_width is not None:
        garment.waist_width = waist_width

    if hip_width is not None:
        garment.hip_width = hip_width

    if shoulder_width is not None:
        garment.shoulder_width = shoulder_width

    if inseam is not None:
        garment.inseam = inseam

    # --------------------------------------------------------
    # Save Changes
    # --------------------------------------------------------

    try:
        db.commit()
        db.refresh(garment)

    except Exception as exc:
        db.rollback()

        raise RuntimeError(
            "Unable to update the garment record."
        ) from exc

    return garment


# ============================================================
# Delete Garment
# ============================================================

def delete_garment(
    db: Session,
    garment_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """
    Delete a garment owned by the authenticated user.

    Args:
        db:
            Active SQLAlchemy database session.

        garment_id:
            UUID of the garment to delete.

        user_id:
            UUID of the authenticated retailer.

    Returns:
        bool:
            True if the garment was deleted.
            False if the garment does not exist or does not
            belong to the authenticated user.
    """

    # --------------------------------------------------------
    # Find Garment and Verify Ownership
    # --------------------------------------------------------

    garment = (
        db.query(Garment)
        .filter(
            Garment.garment_id == garment_id,
            Garment.user_id == user_id,
        )
        .first()
    )

    if garment is None:
        return False

    # --------------------------------------------------------
    # Delete Garment
    # --------------------------------------------------------

    try:
        db.delete(garment)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise RuntimeError(
            "Unable to delete the garment record."
        ) from exc

    return True