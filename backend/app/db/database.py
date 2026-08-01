"""
Database configuration and SQLAlchemy setup for SmartFit.

This module is responsible for:

1. Creating the SQLAlchemy database engine.
2. Creating a database session factory.
3. Providing the declarative base class used by SQLAlchemy models.

The database connection URL is retrieved from the application
configuration defined in app.core.config.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Determine which database should be used.
#
# By default, SmartFit uses the development database.
#
# When SMARTFIT_ENV=test is defined, the application connects
# to the isolated PostgreSQL test database instead.
#
database_url = (
    settings.TEST_DATABASE_URL
    if os.getenv("SMARTFIT_ENV") == "test"
    else settings.DATABASE_URL
)


# Create the SQLAlchemy engine.
#
# The engine manages communication between SmartFit and the
# selected PostgreSQL database.
engine = create_engine(
    database_url
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