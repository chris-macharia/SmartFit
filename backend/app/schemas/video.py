"""
Pydantic schemas for SmartFit video operations.

This module defines the request and response schemas used by
the video API.

Video files themselves are uploaded using FastAPI's UploadFile
and multipart/form-data mechanism.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VideoResponse(BaseModel):
    """
    Response schema for a stored SmartFit video.

    The actual video binary data is not returned by the API.
    The database stores the path to the uploaded video file.
    """

    # Unique identifier of the video.
    video_id: UUID

    # UUID of the user who owns the video.
    user_id: UUID

    # Location of the stored video file.
    video_path: str

    # Current processing status of the video.
    #
    # Examples:
    # - uploaded
    # - processing
    # - completed
    # - failed
    processing_status: str

    # User-provided height used to calibrate measurement estimates.
    user_height_cm: float | None

    # User-safe message explaining why processing failed, if it did.
    processing_error: str | None

    # Date and time when the video was originally uploaded.
    uploaded_at: datetime

    # Allow Pydantic to read values directly from
    # the SQLAlchemy Video model.
    model_config = ConfigDict(
        from_attributes=True,
    )
