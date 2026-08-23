"""
Garment database model for SmartFit.

This module defines the Garment entity used to store clothing
measurements registered by retailers.

The Garment model corresponds to the current Garments entity
defined in the SmartFit database design.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Garment(Base):
    """
    SQLAlchemy model representing a garment in SmartFit.

    A garment belongs to the user who uploaded it. Only users
    registered with the "retailer" role should be allowed to
    create garments through the API.

    The current version intentionally stores only the garment
    measurements required for the initial virtual-fitting
    workflow. Additional garment information can be added in
    future versions.
    """

    __tablename__ = "garments"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    # Generate a unique UUID for each garment.
    garment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # --------------------------------------------------------
    # Garment Uploader
    # --------------------------------------------------------

    # Identify the user who uploaded the garment.
    #
    # The authenticated user's ID will be assigned by the
    # backend when the garment is created.
    #
    # The frontend should NOT be trusted to provide this value.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # --------------------------------------------------------
    # Garment Measurements
    # --------------------------------------------------------

    # Chest width in centimetres.
    chest_width: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # Waist width in centimetres.
    waist_width: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # Hip width in centimetres.
    hip_width: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # Shoulder width in centimetres.
    shoulder_width: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # Inseam length in centimetres.
    inseam: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # --------------------------------------------------------
    # Creation Timestamp
    # --------------------------------------------------------

    # Store the date and time when the garment was registered.
    #
    # A timezone-aware UTC timestamp is used to ensure
    # consistent timestamps regardless of server location.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # Many garments can belong to one user.
    user = relationship(
        "User",
        back_populates="garments",
    )