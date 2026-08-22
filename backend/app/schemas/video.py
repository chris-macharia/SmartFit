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


class BodyMeasurementResponse(BaseModel):
    """
    Response schema for body measurements generated from a video.

    Chest, waist, and hip measurements are nullable because the
    current pose-based estimator does not calculate those values yet.
    """

    # Unique identifier of the body measurement record.
    measurement_id: UUID

    # Video used to generate these measurements.
    video_id: UUID

    # Estimated body height in centimetres.
    height: float

    # Estimated chest circumference.
    chest: float | None

    # Estimated waist circumference.
    waist: float | None

    # Estimated hip circumference.
    hips: float | None

    # Estimated shoulder width in centimetres.
    shoulder_width: float

    # Estimated inseam in centimetres.
    inseam: float

    # Confidence score between 0 and 1.
    confidence_score: float

    # Version of the measurement algorithm used.
    processing_version: str

    # Date and time when the measurement was created.
    created_at: datetime

    # Allow Pydantic to read directly from SQLAlchemy models.
    model_config = ConfigDict(
        from_attributes=True,
    )


class VideoResponse(BaseModel):
    """
    Response schema for a stored SmartFit video.

    The actual video binary data is not returned by the API.
    The database stores the path to the uploaded video file.

    When processing is complete, the generated body measurement
    is included in the response.
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

    # Body measurements generated from this video.
    #
    # This remains null while the video is still being processed
    # or if processing fails.
    measurement: BodyMeasurementResponse | None = None

    # Allow Pydantic to read values directly from
    # the SQLAlchemy Video model.
    model_config = ConfigDict(
        from_attributes=True,
    )