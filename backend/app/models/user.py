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

    A user can have multiple uploaded videos and garments.

    Users can currently have one of two roles:

    - customer
    - retailer
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

    # Securely hashed password.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # User role.
    #
    # Supported roles:
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
    videos = relationship(
        "Video",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # One user can upload many garments.
    #
    # Garments uploaded by a customer should be prevented at
    # the API authorization level. The database relationship
    # itself remains user-based.
    garments = relationship(
        "Garment",
        back_populates="user",
        cascade="all, delete-orphan",
    )