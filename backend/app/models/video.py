"""
Video database model for SmartFit.

This module defines the Video entity used to store information
about body videos uploaded by SmartFit users.

The Video model corresponds to the Videos entity defined in the
SmartFit database design.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Video(Base):
    """
    SQLAlchemy model representing a user-uploaded body video.

    Each Video belongs to exactly one User and may have one
    BodyMeasurement record generated from its processing.
    """

    __tablename__ = "videos"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # --------------------------------------------------------
    # User Foreign Key
    # --------------------------------------------------------

    # Identifies the user who uploaded the video.
    #
    # This is a foreign key referencing users.user_id.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # --------------------------------------------------------
    # Video Information
    # --------------------------------------------------------

    # Path to the physical video file.
    video_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Current state of video processing.
    #
    # Possible values include:
    # - uploaded
    # - processing
    # - completed
    # - failed
    processing_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Height supplied by the user in centimetres.
    #
    # A standard camera video has no reliable real-world scale
    # by itself. This value calibrates the normalized pose
    # landmarks produced by the computer-vision pipeline.
    user_height_cm: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # Safe, user-facing explanation when processing cannot finish.
    #
    # Detailed technical exceptions are logged on the server instead
    # of being exposed to the frontend.
    processing_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Date and time when the video was uploaded.
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # Each video belongs to one user.
    user = relationship(
        "User",
        back_populates="videos",
    )

    # A video can produce one body measurement record.
    #
    # The BodyMeasurement is derived from this video, so it should
    # not continue to exist after the source video is deleted.
    #
    # cascade="all, delete-orphan" ensures SQLAlchemy removes the
    # associated measurement when the Video is deleted.
    measurement = relationship(
        "BodyMeasurement",
        back_populates="video",
        uselist=False,
        cascade="all, delete-orphan",
    )