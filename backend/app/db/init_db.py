"""
Database initialization module for SmartFit.

This module is responsible for creating database tables defined
by the SQLAlchemy models.

It is intended to be used during the initial development and
database setup process.
"""

from app.db.database import Base, engine

# Import the models so that SQLAlchemy registers their tables
# with Base.metadata before create_all() is executed.
#
# Without importing the models, SQLAlchemy may not know about
# the tables that need to be created.
from app.models import Garment, User


def init_db():
    """
    Create all database tables defined by the SQLAlchemy models.

    Base.metadata.create_all() checks the database for the tables
    registered with the shared SQLAlchemy Base. Tables that do not
    already exist are created automatically.

    Existing tables are not deleted or modified by this operation.
    """

    # Create all tables registered with Base.metadata.
    #
    # The engine specifies the PostgreSQL database where the
    # tables will be created.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # Run database initialization when this file is executed
    # directly from the command line.
    init_db()

    print("Database tables initialized successfully.")