"""
Body measurement database model for SmartFit.

This module defines the BodyMeasurement entity used to store
body measurements estimated from a user's uploaded body video.

The BodyMeasurement model corresponds to the BodyMeasurements
entity defined in the SmartFit database design.

The measurements are expected to be produced by the SmartFit
computer vision processing pipeline after analyzing an uploaded
body video.
"""

import uuid

from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class BodyMeasurement(Base):
    """
    SQLAlchemy model representing body measurements estimated
    from a user's uploaded body video.

    Each BodyMeasurement record stores the physical measurements
    required by SmartFit for downstream functionality such as:

    - Generating a personalized digital avatar.
    - Recommending appropriate clothing sizes.
    - Supporting virtual clothing fitting.

    The video_id field identifies the video from which the
    measurements were generated. The foreign-key relationship
    will be implemented later when the database relationships
    are refined.
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "body_measurements"

    # Generate a unique UUID for each body measurement record.
    #
    # UUIDs provide globally unique identifiers for measurement
    # records and are consistent with the documented database design.
    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Store the UUID of the video used to generate these measurements.
    #
    # This field is currently stored as a UUID without a foreign-key
    # constraint. The relationship will be refined later when the
    # database entity relationships are finalized.
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the user's estimated height.
    #
    # Numeric is used for decimal measurements to provide precise
    # values without floating-point rounding issues.
    height: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the estimated chest measurement.
    chest: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the estimated waist measurement.
    waist: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the estimated hip measurement.
    hips: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the estimated shoulder width.
    shoulder_width: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the estimated inseam measurement.
    inseam: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )