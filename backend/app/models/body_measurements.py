"""
Body measurement database model for SmartFit.

This module defines the BodyMeasurement entity used to store
body measurements estimated from a user's uploaded body video.

The BodyMeasurement model corresponds to the BodyMeasurements
entity defined in the SmartFit database design.

The measurements are produced by the SmartFit computer vision
processing pipeline after analyzing an uploaded body video.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class BodyMeasurement(Base):
    """
    SQLAlchemy model representing body measurements estimated
    from a user's uploaded body video.

    Each BodyMeasurement belongs to exactly one Video.

    A video can have at most one BodyMeasurement because the
    measurement represents the result of processing that video.
    """

    __tablename__ = "body_measurements"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # --------------------------------------------------------
    # Video Foreign Key
    # --------------------------------------------------------

    # Store the UUID of the video used to generate these measurements.
    #
    # The foreign key uses ON DELETE CASCADE because a measurement
    # has no purpose after its source video has been deleted.
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "videos.video_id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    # --------------------------------------------------------
    # Body Measurements
    # --------------------------------------------------------

    # Store the user's estimated height.
    height: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Estimated chest measurement.
    chest: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # Estimated waist measurement.
    waist: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # Estimated hip measurement.
    hips: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    # Estimated shoulder width.
    shoulder_width: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Estimated inseam.
    inseam: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # --------------------------------------------------------
    # Processing Metadata
    # --------------------------------------------------------

    # Value between 0 and 1 representing the reliability of
    # the generated measurement estimates.
    confidence_score: Mapped[float] = mapped_column(
        Numeric(3, 2),
        nullable=False,
        default=0,
    )

    # Identifies the measurement algorithm used.
    #
    # This allows future algorithm versions to remain traceable.
    processing_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pose-v1",
    )

    # Timestamp recording when SmartFit created the measurement.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # Each measurement belongs to exactly one video.
    #
    # The relationship mirrors Video.measurement.
    video = relationship(
        "Video",
        back_populates="measurement",
    )

    # A measurement can be used to generate one avatar.
    #
    # The Avatar is derived from the measurement, so it should
    # be removed when the measurement is removed.
    avatar = relationship(
        "Avatar",
        back_populates="measurement",
        uselist=False,
        cascade="all, delete-orphan",
    )