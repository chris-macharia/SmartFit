"""
Tests for the SmartFit Video database model.

This module verifies that the Video SQLAlchemy model is correctly
registered with the application's database metadata and that the
expected database table and columns are defined.
"""

from app.db.database import Base
from app.models import Video


def test_video_table_is_registered():
    """
    Verify that the Video model is registered with SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the videos table exists in SQLAlchemy's metadata.
    assert "videos" in Base.metadata.tables


def test_video_table_columns():
    """
    Verify that the videos table contains all expected columns.

    The columns tested here correspond to the original SmartFit
    Videos table design.
    """

    # Retrieve the videos table definition from SQLAlchemy metadata.
    videos_table = Base.metadata.tables["videos"]

    # Define the columns expected in the SmartFit Videos table.
    expected_columns = {
        "video_id",
        "user_id",
        "video_path",
        "processing_status",
        "uploaded_at",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(videos_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)