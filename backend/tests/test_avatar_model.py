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


def test_avatar_measurement_id_is_foreign_key():
    """
    Verify that avatars.measurement_id references
    body_measurements.measurement_id.

    This confirms that the Avatar model correctly implements
    the BodyMeasurement-to-Avatar relationship defined in the ERD.
    """

    # Retrieve the avatars table from SQLAlchemy metadata.
    avatars_table = Base.metadata.tables["avatars"]

    # Retrieve the measurement_id column.
    measurement_id_column = avatars_table.columns["measurement_id"]

    # Retrieve the foreign keys associated with measurement_id.
    foreign_keys = list(measurement_id_column.foreign_keys)

    # Confirm that exactly one foreign key exists.
    assert len(foreign_keys) == 1

    # Confirm that the foreign key references
    # body_measurements.measurement_id.
    assert (
        foreign_keys[0].target_fullname
        == "body_measurements.measurement_id"
    )    


def test_avatar_measurement_id_is_unique():
    """
    Verify that measurement_id is unique.

    The original ERD defines a one-to-one relationship between
    BodyMeasurements and Avatars. Therefore, one BodyMeasurement
    cannot have multiple Avatar records.
    """

    # Retrieve the avatars table.
    avatars_table = Base.metadata.tables["avatars"]

    # Retrieve the measurement_id column.
    measurement_id_column = avatars_table.columns["measurement_id"]

    # Confirm that the column is unique.
    assert measurement_id_column.unique is True    