"""
SQLAlchemy declarative base for SmartFit database models.

This module provides the shared Base class that all SQLAlchemy
database models in the SmartFit application will inherit from.

Using a common Base allows SQLAlchemy to keep track of all
database models through a single metadata object.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SmartFit SQLAlchemy models.

    Every database model created for the SmartFit application
    should inherit from this class.

    SQLAlchemy uses the metadata associated with this Base class
    to keep track of the database tables defined by the application.
    """

    pass