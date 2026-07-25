"""
Virtual fitting database model for SmartFit.

This module defines the VirtualFitting entity used to store
the results of virtual clothing fitting operations.

The VirtualFitting model corresponds to the VirtualFittings
entity defined in the SmartFit database design.

A virtual fitting combines:

- A SmartFit user.
- A registered garment.
- A generated digital avatar.

The system uses these inputs to determine a recommended
clothing size and produce a fit result.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class VirtualFitting(Base):
    """
    SQLAlchemy model representing a virtual clothing fitting result.

    Each VirtualFitting record stores the user, garment, and avatar
    involved in a fitting session, along with the recommended clothing
    size and the resulting fit assessment.

    The user_id, garment_id, and avatar_id fields currently store
    UUID values without enforced foreign-key constraints. These
    relationships will be refined later when the complete database
    relationship strategy is finalized.
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "virtual_fittings"

    # Generate a unique UUID for each virtual fitting record.
    #
    # UUIDs provide globally unique identifiers for virtual fitting
    # records and are consistent with the documented database design.
    fitting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Store the UUID of the user who performs the virtual fitting.
    #
    # This field is currently stored as a UUID without a foreign-key
    # constraint. The relationship will be refined later.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the UUID of the garment being evaluated.
    #
    # This field identifies the garment selected for the virtual
    # fitting operation.
    garment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the UUID of the digital avatar used during the fitting.
    #
    # The avatar represents the user's estimated body shape and
    # dimensions.
    avatar_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Store the clothing size recommended by the fitting process.
    #
    # Examples could include:
    # - Small
    # - Medium
    # - Large
    # - XL
    #
    # The exact recommendation logic will be implemented later
    # as part of the SmartFit fitting functionality.
    recommended_size: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Store the result of the virtual fitting operation.
    #
    # Examples could include:
    # - Good Fit
    # - Tight
    # - Loose
    #
    # The exact result categories will be defined when the
    # virtual fitting functionality is implemented.
    fit_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Store the date and time when the virtual fitting was performed.
    #
    # A timezone-aware UTC timestamp is used to ensure that timestamps
    # remain consistent regardless of the server's local timezone.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )