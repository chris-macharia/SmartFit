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
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    """
    SQLAlchemy model representing a SmartFit user.

    Each user is assigned a UUID as their primary key. UUIDs are used
    consistently throughout the SmartFit database design to identify
    users and related records.
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "users"

    # Generate a unique UUID for each user.
    #
    # UUIDs provide globally unique identifiers and are consistent
    # with the UUID-based identifiers used throughout the SmartFit
    # database design.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Store the user's full name.
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Store the user's email address.
    #
    # The email must be unique so that two accounts cannot be
    # registered using the same email address.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    # Store the securely hashed version of the user's password.
    #
    # Plain-text passwords must never be stored in the database.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Store the user's role within the SmartFit system.
    #
    # Examples include:
    # - customer
    # - retailer
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Store the date and time when the user account was created.
    #
    # A timezone-aware UTC timestamp is used to ensure consistent
    # timestamps regardless of the server's local timezone.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )