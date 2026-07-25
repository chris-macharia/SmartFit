"""
Tests for the SmartFit BodyMeasurement database model.

This module verifies that the BodyMeasurement SQLAlchemy model
is correctly registered with the application's database metadata
and that all expected database columns are defined.
"""

from app.db.database import Base
from app.models import BodyMeasurement


def test_body_measurement_table_is_registered():
    """
    Verify that the BodyMeasurement model is registered with
    SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the body_measurements table exists in
    # SQLAlchemy's metadata.
    assert "body_measurements" in Base.metadata.tables


def test_body_measurement_table_columns():
    """
    Verify that the body_measurements table contains all
    expected columns.

    The columns tested here correspond to the original SmartFit
    BodyMeasurements table design.
    """

    # Retrieve the body_measurements table definition from
    # SQLAlchemy metadata.
    body_measurements_table = Base.metadata.tables["body_measurements"]

    # Define the columns expected in the SmartFit
    # BodyMeasurements table.
    expected_columns = {
        "measurement_id",
        "video_id",
        "height",
        "chest",
        "waist",
        "hips",
        "shoulder_width",
        "inseam",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(body_measurements_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)