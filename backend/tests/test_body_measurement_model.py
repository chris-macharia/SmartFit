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


def test_body_measurement_video_id_is_foreign_key():
    """
    Verify that body_measurements.video_id references videos.video_id.

    This confirms that the BodyMeasurement model correctly implements
    the Video-to-BodyMeasurement relationship defined in the ERD.
    """

    # Retrieve the body_measurements table from SQLAlchemy metadata.
    body_measurements_table = Base.metadata.tables[
        "body_measurements"
    ]

    # Retrieve the video_id column.
    video_id_column = body_measurements_table.columns["video_id"]

    # Retrieve the foreign keys associated with video_id.
    foreign_keys = list(video_id_column.foreign_keys)

    # Confirm that exactly one foreign key exists.
    assert len(foreign_keys) == 1

    # Confirm that the foreign key references videos.video_id.
    assert foreign_keys[0].target_fullname == "videos.video_id"    


def test_body_measurement_video_id_is_unique():
    """
    Verify that video_id is unique.

    The original ERD defines a one-to-one relationship between
    Videos and BodyMeasurements. Therefore, one Video cannot
    have multiple BodyMeasurement records.
    """

    # Retrieve the body_measurements table.
    body_measurements_table = Base.metadata.tables[
        "body_measurements"
    ]

    # Retrieve the video_id column.
    video_id_column = body_measurements_table.columns["video_id"]

    # Confirm that the column is unique.
    assert video_id_column.unique is True    