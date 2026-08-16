"""
Video database model for SmartFit.

This module defines the Video entity used to store information
about body videos uploaded by SmartFit users.

The Video model corresponds to the Videos entity defined in the
SmartFit database design.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Video(Base):
    """
    SQLAlchemy model representing a user-uploaded body video.

    Each Video belongs to exactly one User.
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