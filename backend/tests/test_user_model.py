"""
Tests for the SmartFit User database model.

This module verifies that the User SQLAlchemy model is correctly
registered with the application's database metadata and that
the expected database table and columns are defined.
"""

from app.db.database import Base
from app.models import User


def test_user_table_is_registered():
    """
    Verify that the User model is registered with SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the users table exists in SQLAlchemy's metadata.
    assert "users" in Base.metadata.tables


def test_user_table_columns():
    """
    Verify that the users table contains all expected columns.

    The columns tested here correspond to the original SmartFit
    User table design.
    """

    # Retrieve the users table definition from SQLAlchemy metadata.
    users_table = Base.metadata.tables["users"]

    # Define the columns expected in the SmartFit User table.
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