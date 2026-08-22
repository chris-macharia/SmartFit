"""
Tests for SmartFit avatar Pydantic schemas.

This module verifies that AvatarResponse correctly validates
avatar data and can be created from SQLAlchemy model attributes.
"""

import uuid
from datetime import datetime, timezone

from app.models.avatar import Avatar
from app.schemas.avatar import AvatarResponse


# ============================================================
# AvatarResponse Tests
# ============================================================


def test_avatar_response_accepts_valid_data():
    """
    Verify that AvatarResponse accepts a valid avatar payload.
    """

    avatar_id = uuid.uuid4()
    measurement_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)

    response = AvatarResponse(
        avatar_id=avatar_id,
        measurement_id=measurement_id,
        avatar_path="uploads/avatars/test-avatar.glb",
        created_at=created_at,
    )

    assert response.avatar_id == avatar_id
    assert response.measurement_id == measurement_id
    assert (
        response.avatar_path
        == "uploads/avatars/test-avatar.glb"
    )
    assert response.created_at == created_at


def test_avatar_response_can_read_from_sqlalchemy_model():
    """
    Verify that AvatarResponse can be created directly from
    an Avatar SQLAlchemy model.
    """

    avatar_id = uuid.uuid4()
    measurement_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)

    avatar = Avatar(
        avatar_id=avatar_id,
        measurement_id=measurement_id,
        avatar_path="uploads/avatars/test-avatar.glb",
        created_at=created_at,
    )

    response = AvatarResponse.model_validate(
        avatar
    )

    assert response.avatar_id == avatar_id
    assert response.measurement_id == measurement_id
    assert (
        response.avatar_path
        == "uploads/avatars/test-avatar.glb"
    )
    assert response.created_at == created_at