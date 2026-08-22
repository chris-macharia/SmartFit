"""
Pydantic schemas for SmartFit avatar operations.

This module defines the request and response schemas used by
the avatar API.

Avatars are generated from body measurements produced by the
SmartFit body measurement processing pipeline.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AvatarResponse(BaseModel):
    """
    Response schema for a stored SmartFit avatar.

    The actual avatar file is not returned by the API.
    The database stores the path to the generated avatar file.
    """

    # Unique identifier of the avatar.
    avatar_id: UUID

    # UUID of the body measurement record used
    # to generate this avatar.
    measurement_id: UUID

    # Location of the stored avatar file.
    avatar_path: str

    # Date and time when the avatar was generated.
    created_at: datetime

    # Allow Pydantic to read values directly from
    # the SQLAlchemy Avatar model.
    model_config = ConfigDict(
        from_attributes=True,
    )