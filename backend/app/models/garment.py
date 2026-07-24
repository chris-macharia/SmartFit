"""
Garment database model for SmartFit.

This module defines the Garment entity used to store clothing
information registered by retailers.

The Garment model corresponds to the Garments entity defined
in the SmartFit database design.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Garment(Base):
    """
    SQLAlchemy model representing a garment in SmartFit.

    Each garment contains information about the clothing item,
    including its category, brand, size, physical measurements,
    and associated image.

    The retailer_id field identifies the retailer who registered
    the garment. The foreign-key relationship will be implemented
    later when the User and retailer database design is refined.
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "garments"

    # Generate a unique UUID for each garment.
    #
    # UUIDs are used instead of sequential integer IDs to provide
    # globally unique identifiers for garment records.
    garment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Store the UUID of the retailer who registered the garment.
    #
    # This field is currently stored as a UUID without a foreign-key
    # constraint. The relationship will be refined later when the
    # User and retailer database design is updated.
    retailer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the name of the garment.
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Store the garment category.
    #
    # Examples may include:
    # - Shirt
    # - Trousers
    # - Dress
    # - Jacket
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Store the brand associated with the garment.
    brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Store the garment's size.
    #
    # Examples may include:
    # - XS
    # - S
    # - M
    # - L
    # - XL
    size: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Store the chest measurement of the garment.
    #
    # Numeric is used instead of Float because garment measurements
    # represent precise decimal values and should not be affected
    # by floating-point rounding errors.
    chest: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the waist measurement of the garment.
    waist: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the hip measurement of the garment.
    hips: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the garment length.
    length: Mapped[float] = mapped_column(
        Numeric,
        nullable=False,
    )

    # Store the path or location of the garment image.
    #
    # The actual image file will be handled separately by the
    # application's file storage system. This field stores the
    # reference to where the image can be accessed.
    image_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Store the date and time when the garment was registered.
    #
    # A timezone-aware UTC timestamp is used to ensure consistent
    # timestamps regardless of the server's local timezone.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )