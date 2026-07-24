"""
Tests for the SmartFit Garment database model.

This module verifies that the Garment SQLAlchemy model is correctly
registered with the application's database metadata and that the
expected database table and columns are defined.
"""

from app.db.database import Base
from app.models import Garment


def test_garment_table_is_registered():
    """
    Verify that the Garment model is registered with SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the garments table exists in SQLAlchemy's metadata.
    assert "garments" in Base.metadata.tables


def test_garment_table_columns():
    """
    Verify that the garments table contains all expected columns.

    The columns tested here correspond to the original SmartFit
    Garments table design.
    """

    # Retrieve the garments table definition from SQLAlchemy metadata.
    garments_table = Base.metadata.tables["garments"]

    # Define the columns expected in the SmartFit Garments table.
    expected_columns = {
        "garment_id",
        "retailer_id",
        "name",
        "category",
        "brand",
        "size",
        "chest",
        "waist",
        "hips",
        "length",
        "image_path",
        "created_at",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(garments_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)