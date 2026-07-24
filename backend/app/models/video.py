"""
Video database model for SmartFit.

This module defines the Video entity used to store information
about body videos uploaded by SmartFit users.

The Video model corresponds to the Videos entity defined in the
SmartFit database design.

The uploaded video is expected to be processed by the computer
vision module to estimate the user's body measurements.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Video(Base):
    """
    SQLAlchemy model representing a user-uploaded body video.

    Each Video record stores the location of an uploaded video
    and tracks its processing status.

    The user_id field identifies the user who uploaded the video.
    The foreign-key relationship will be implemented later when
    the User database design is refined.
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "videos"

    # Generate a unique UUID for each uploaded video.
    #
    # UUIDs provide globally unique identifiers for video records
    # and are consistent with the documented database design.
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Store the UUID of the user who uploaded the video.
    #
    # This field is currently stored as a UUID without a foreign-key
    # constraint. The relationship will be refined later when the
    # User database design is updated.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the path or location of the uploaded video file.
    #
    # The actual video file will be handled by the application's
    # file storage system. This field stores the reference to
    # where the video can be accessed.
    video_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Store the current processing status of the video.
    #
    # Examples of possible statuses include:
    # - uploaded
    # - processing
    # - completed
    # - failed
    #
    # The exact status workflow will be implemented when the
    # computer vision processing pipeline is developed.
    processing_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Store the date and time when the video was uploaded.
    #
    # A timezone-aware UTC timestamp is used to ensure that
    # timestamps remain consistent regardless of the server's
    # local timezone.
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )