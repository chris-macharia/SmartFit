"""
Tests for the SmartFit Avatar database model.

This module verifies that the Avatar SQLAlchemy model is correctly
registered with the application's database metadata and that all
expected database columns are defined.
"""

from app.db.database import Base
from app.models import Avatar


def test_avatar_table_is_registered():
    """
    Verify that the Avatar model is registered with SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the avatars table exists in SQLAlchemy metadata.
    assert "avatars" in Base.metadata.tables


def test_avatar_table_columns():
    """
    Verify that the avatars table contains all expected columns.

    The columns tested here correspond to the original SmartFit
    Avatars table design.
    """

    # Retrieve the avatars table definition from SQLAlchemy metadata.
    avatars_table = Base.metadata.tables["avatars"]

    # Define the columns expected in the SmartFit Avatars table.
    expected_columns = {
        "avatar_id",
        "measurement_id",
        "avatar_path",
        "created_at",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(avatars_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)