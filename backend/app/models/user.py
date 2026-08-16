"""
User database model for SmartFit.

This module defines the User entity used to store account information
for customers and retailers using the SmartFit system.

The User model corresponds to the Users entity defined in the
SmartFit database design.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """
    SQLAlchemy model representing a SmartFit user.

    A user can have multiple uploaded videos.
    """

    __tablename__ = "users"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # --------------------------------------------------------
    # User Information
    # --------------------------------------------------------

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    # Store the securely hashed password.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # User role, for example:
    # - customer
    # - retailer
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # --------------------------------------------------------
    # Account Creation Timestamp
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    # One user can upload many videos.
    #
    # The cascade option ensures that when a User is deleted
    # through SQLAlchemy, their associated Video records are
    # also deleted.
    videos = relationship(
        "Video",
        back_populates="user",
        cascade="all, delete-orphan",
    )