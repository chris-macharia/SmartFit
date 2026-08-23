"""
Tests for the SmartFit Garment database model.

This module verifies that the Garment SQLAlchemy model is correctly
registered with the application's database metadata and that the
current garment table structure is correctly defined.
"""

from app.db.database import Base
from app.models import Garment


def test_garment_table_is_registered():
    """
    Verify that the Garment model is registered with SQLAlchemy metadata.
    """

    # Confirm that the garments table exists in SQLAlchemy metadata.
    assert "garments" in Base.metadata.tables


def test_garment_table_columns():
    """
    Verify that the garments table contains the current expected columns.
    """

    # Retrieve the garments table definition.
    garments_table = Base.metadata.tables["garments"]

    # Define the columns expected in the current Garments table.
    expected_columns = {
        "garment_id",
        "user_id",
        "chest_width",
        "waist_width",
        "hip_width",
        "shoulder_width",
        "inseam",
        "created_at",
    }

    # Retrieve the actual columns registered by SQLAlchemy.
    actual_columns = set(garments_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)


def test_garment_user_id_is_foreign_key():
    """
    Verify that garments.user_id references users.user_id.

    This establishes the relationship between the user who uploaded
    the garment and the garment record.
    """

    # Retrieve the garments table.
    garments_table = Base.metadata.tables["garments"]

    # Retrieve the user_id column.
    user_id_column = garments_table.columns["user_id"]

    # Retrieve foreign keys associated with user_id.
    foreign_keys = list(user_id_column.foreign_keys)

    # Confirm that exactly one foreign key exists.
    assert len(foreign_keys) == 1

    # Confirm that the foreign key references users.user_id.
    assert foreign_keys[0].target_fullname == "users.user_id"