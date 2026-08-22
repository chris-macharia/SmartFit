"""
Avatar service for SmartFit.

This module contains the database and application logic used by
the avatar API.

Avatar generation is intentionally separate from video processing.
A completed BodyMeasurement is used as the input to an explicit
avatar-generation operation.
"""

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.avatar import Avatar
from app.models.body_measurements import BodyMeasurement
from app.models.video import Video
from app.services.avatar_generator import (
    AvatarGenerationError,
    generate_avatar_glb,
)


# ============================================================
# Avatar Storage
# ============================================================

AVATAR_STORAGE_DIR = Path(
    "uploads/avatars"
)

AVATAR_STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Retrieve Avatar
# ============================================================

def get_avatar_by_id(
    db: Session,
    avatar_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Avatar | None:
    """
    Retrieve an avatar by ID if it belongs to the authenticated user.

    Avatar ownership is established through:

        Avatar
            ↓
        BodyMeasurement
            ↓
        Video
            ↓
        User

    Args:
        db:
            Active SQLAlchemy database session.

        avatar_id:
            UUID of the requested avatar.

        user_id:
            UUID of the authenticated user.

    Returns:
        The Avatar if it exists and belongs to the user.
        Otherwise None.
    """

    return (
        db.query(Avatar)
        .join(
            BodyMeasurement,
            Avatar.measurement_id
            == BodyMeasurement.measurement_id,
        )
        .join(
            Video,
            BodyMeasurement.video_id
            == Video.video_id,
        )
        .filter(
            Avatar.avatar_id == avatar_id,
            Video.user_id == user_id,
        )
        .first()
    )


# ============================================================
# Create Avatar
# ============================================================

def create_avatar(
    db: Session,
    measurement_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Avatar:
    """
    Generate and persist an avatar from a user's body measurement.

    The body measurement must belong to a video owned by the
    authenticated user.

    Args:
        db:
            Active SQLAlchemy database session.

        measurement_id:
            UUID of the body measurement used to generate
            the avatar.

        user_id:
            UUID of the authenticated user.

    Returns:
        The newly created Avatar.

    Raises:
        ValueError:
            If the measurement does not exist, does not belong
            to the authenticated user, or already has an avatar.

        AvatarGenerationError:
            If the measurements cannot produce an avatar.
    """

    # --------------------------------------------------------
    # Find the measurement and verify ownership.
    # --------------------------------------------------------

    measurement = (
        db.query(BodyMeasurement)
        .join(
            Video,
            BodyMeasurement.video_id
            == Video.video_id,
        )
        .filter(
            BodyMeasurement.measurement_id == measurement_id,
            Video.user_id == user_id,
        )
        .first()
    )

    if measurement is None:
        raise ValueError(
            "Body measurement not found."
        )

    # --------------------------------------------------------
    # Prevent duplicate avatars.
    # --------------------------------------------------------

    existing_avatar = (
        db.query(Avatar)
        .filter(
            Avatar.measurement_id == measurement_id,
        )
        .first()
    )

    if existing_avatar is not None:
        raise ValueError(
            "An avatar already exists for this body measurement."
        )

    # --------------------------------------------------------
    # Generate the GLB.
    # --------------------------------------------------------

    glb_data = generate_avatar_glb(
        measurement
    )

    # --------------------------------------------------------
    # Generate a unique file path.
    # --------------------------------------------------------

    avatar_id = uuid.uuid4()

    filename = f"{avatar_id}.glb"

    file_path = (
        AVATAR_STORAGE_DIR / filename
    )

    # --------------------------------------------------------
    # Save the physical avatar file.
    # --------------------------------------------------------

    try:
        file_path.write_bytes(glb_data)

    except Exception as exc:
        raise RuntimeError(
            "Unable to save the generated avatar."
        ) from exc

    # --------------------------------------------------------
    # Create database record.
    # --------------------------------------------------------

    avatar = Avatar(
        avatar_id=avatar_id,
        measurement_id=measurement.measurement_id,
        avatar_path=str(file_path),
    )

    try:
        db.add(avatar)
        db.commit()
        db.refresh(avatar)

    except Exception as exc:
        db.rollback()

        # Do not leave an orphaned GLB file if the
        # database transaction fails.
        if file_path.exists():
            file_path.unlink()

        raise RuntimeError(
            "Unable to create the avatar record."
        ) from exc

    return avatar