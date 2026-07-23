"""
Database configuration and SQLAlchemy setup for SmartFit.

This module is responsible for:

1. Creating the SQLAlchemy database engine.
2. Creating a database session factory.
3. Providing the declarative base class used by SQLAlchemy models.

The database connection URL is retrieved from the application
configuration defined in app.core.config.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# Create the SQLAlchemy engine.
#
# The engine manages communication between the SmartFit backend
# and the PostgreSQL database.
#
# The connection URL is retrieved from the environment through
# the application settings object.
engine = create_engine(
    settings.DATABASE_URL
)


# Create a database session factory.
#
# SessionLocal will be used to create individual database sessions
# whenever the application needs to communicate with PostgreSQL.
#
# autocommit=False:
#   Database changes must be explicitly committed by the application.
#
# autoflush=False:
#   SQLAlchemy will not automatically flush pending changes before
#   every database operation.
#
# bind=engine:
#   Each session created by this factory will use our PostgreSQL
#   database engine.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Create the SQLAlchemy declarative base.
#
# All SmartFit database models will inherit from this Base class.
# SQLAlchemy uses the Base class to keep track of the application's
# database table definitions.
#
# For example:
#
#     class User(Base):
#         ...
#
Base = declarative_base()