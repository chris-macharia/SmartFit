"""
Tests for the SmartFit User database model.

This module verifies that the User SQLAlchemy model is correctly
registered with the application's database metadata and that all
expected database columns are defined.
"""

import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base
from app.models import User


def test_user_table_is_registered():
    """
    Verify that the User model is registered with SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the users table exists in SQLAlchemy metadata.
    assert "users" in Base.metadata.tables


def test_user_table_columns():
    """
    Verify that the users table contains all expected columns.

    The columns tested here correspond to the SmartFit User
    database design.
    """

    # Retrieve the users table definition from SQLAlchemy metadata.
    users_table = Base.metadata.tables["users"]

    # Define the columns expected in the SmartFit Users table.
    expected_columns = {
        "id",
        "full_name",
        "email",
        "hashed_password",
        "role",
        "created_at",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(users_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)


def test_user_id_is_uuid():
    """
    Verify that the User primary key uses PostgreSQL UUID.

    UUID identifiers provide globally unique IDs and maintain
    consistency with the UUID-based foreign keys used throughout
    the SmartFit database design.
    """

    # Retrieve the users table from SQLAlchemy metadata.
    users_table = Base.metadata.tables["users"]

    # Retrieve the SQLAlchemy column definition for the primary key.
    id_column = users_table.columns["id"]

    # Confirm that the primary key uses the PostgreSQL UUID type.
    assert isinstance(id_column.type, UUID)

    # Confirm that the primary key is correctly configured.
    assert id_column.primary_key is True