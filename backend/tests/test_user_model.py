"""
Tests for the SmartFit User database model.

This module verifies that the User SQLAlchemy model is correctly
registered with the application's database metadata and that all
expected database columns are defined.
"""

from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base
from app.models import User


def test_user_table_is_registered():
    """
    Verify that the User model is registered with SQLAlchemy metadata.
    """

    # Confirm that the users table exists in SQLAlchemy metadata.
    assert "users" in Base.metadata.tables


def test_user_table_columns():
    """
    Verify that the users table contains all expected columns.
    """

    # Retrieve the users table definition.
    users_table = Base.metadata.tables["users"]

    # Define the expected columns from the SmartFit database design.
    expected_columns = {
        "user_id",
        "full_name",
        "email",
        "hashed_password",
        "role",
        "created_at",
    }

    # Retrieve the actual column names.
    actual_columns = set(users_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)


def test_user_id_is_uuid():
    """
    Verify that the User primary key uses PostgreSQL UUID.
    """

    # Retrieve the users table.
    users_table = Base.metadata.tables["users"]

    # Retrieve the user_id primary key column.
    user_id_column = users_table.columns["user_id"]

    # Confirm that the primary key uses PostgreSQL UUID.
    assert isinstance(user_id_column.type, UUID)

    # Confirm that user_id is the primary key.
    assert user_id_column.primary_key is True