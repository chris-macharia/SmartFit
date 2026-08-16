"""
Pydantic schemas for SmartFit video operations.

This module defines the request and response schemas used by
the video upload API.

The actual video file is uploaded using FastAPI's UploadFile
and multipart/form-data mechanism.

The schemas in this module are therefore mainly responsible
for validating and returning information about stored video
records.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VideoResponse(BaseModel):
    """
    Response schema for a successfully stored video.

    This schema represents the information that SmartFit
    returns to the frontend after a video has been uploaded.

    The actual video binary data is NOT returned in the API
    response. The database record only stores the path to
    the uploaded file.
    """

    # Unique identifier assigned to the uploaded video.
    video_id: UUID

    # UUID of the authenticated user who uploaded the video.
    user_id: UUID

    # Location where the uploaded video has been stored.
    video_path: str

    # Current stage of video processing.
    #
    # Initially this will normally be:
    #
    #     uploaded
    #
    # Later the computer-vision pipeline can update this to:
    #
    #     processing
    #     completed
    #     failed
    processing_status: str

    # Date and time when the video was uploaded.
    uploaded_at: datetime

    # Allow Pydantic to create this response from
    # a SQLAlchemy Video model instance.
    model_config = ConfigDict(
        from_attributes=True
    )