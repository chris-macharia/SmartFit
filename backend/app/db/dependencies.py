"""
Database dependencies for the SmartFit FastAPI application.

This module provides reusable FastAPI dependencies related to
database access.

The get_db() function creates a database session for an incoming
request and ensures that the session is properly closed when the
request is finished.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session to a FastAPI request.

    A new SQLAlchemy session is created when this dependency is
    requested by a route. The session is then provided to the route
    using `yield`.

    The `finally` block ensures that the database session is always
    closed after the request has completed, even if an exception
    occurs while processing the request.

    Yields:
        Session: An active SQLAlchemy database session.
    """

    # Create a new database session using the SessionLocal factory.
    db = SessionLocal()

    try:
        # Provide the active database session to the FastAPI route.
        yield db

    finally:
        # Always close the database session after the request.
        #
        # This releases the database connection and prevents
        # unused connections from accumulating over time.
        db.close()