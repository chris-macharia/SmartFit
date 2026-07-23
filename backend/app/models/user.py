"""
User database model for SmartFit.

This module defines the User entity used to store information
about customers and sellers registered in the SmartFit system.

The User model corresponds to the User table defined in the
SmartFit database design.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    """
    SQLAlchemy model representing a SmartFit user.

    A user can be either a customer or a seller. The role field
    is used to distinguish between the two types of users.

    The model currently contains the following fields:

    - id
    - full_name
    - email
    - hashed_password
    - role
    - created_at
    """

    # Define the name of the PostgreSQL database table.
    __tablename__ = "users"

    # Unique identifier for each user.
    #
    # This field is the primary key of the users table.
    # SQLAlchemy will map this to an integer column in PostgreSQL.
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # Store the user's full name.
    #
    # The field is required and cannot be NULL.
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Store the user's email address.
    #
    # The email is required and must be unique.
    # This prevents multiple accounts from being registered
    # using the same email address.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Store the user's password as a secure hash.
    #
    # The application must NEVER store the user's plain-text
    # password in the database.
    #
    # Password hashing and authentication will be implemented
    # in a later milestone.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Store the user's role within the SmartFit system.
    #
    # The initial roles are:
    # - customer
    # - seller
    #
    # We are using a String for now. This can be refined to
    # an Enum later if stricter role validation is required.
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Store the date and time when the user account was created. 
    # 
    # A timezone-aware UTC timestamp is used so that account creation
    # times are stored consistently regardless of the server's local
    # timezone.
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)