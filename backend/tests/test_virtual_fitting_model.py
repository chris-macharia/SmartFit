"""
Tests for the SmartFit VirtualFitting database model.

This module verifies that the VirtualFitting SQLAlchemy model is
correctly registered with the application's database metadata and
that all expected database columns are defined.
"""

from app.db.database import Base
from app.models import VirtualFitting


def test_virtual_fitting_table_is_registered():
    """
    Verify that the VirtualFitting model is registered with
    SQLAlchemy metadata.

    A registered model means SQLAlchemy is aware of the corresponding
    database table and can include it when creating database tables.
    """

    # Confirm that the virtual_fittings table exists in
    # SQLAlchemy metadata.
    assert "virtual_fittings" in Base.metadata.tables


def test_virtual_fitting_table_columns():
    """
    Verify that the virtual_fittings table contains all expected columns.

    The columns tested here correspond to the original SmartFit
    VirtualFittings table design.
    """

    # Retrieve the virtual_fittings table definition from
    # SQLAlchemy metadata.
    virtual_fittings_table = Base.metadata.tables["virtual_fittings"]

    # Define the columns expected in the SmartFit VirtualFittings table.
    expected_columns = {
        "fitting_id",
        "user_id",
        "garment_id",
        "avatar_id",
        "recommended_size",
        "fit_result",
        "created_at",
    }

    # Retrieve the actual column names registered by SQLAlchemy.
    actual_columns = set(virtual_fittings_table.columns.keys())

    # Confirm that all expected columns are present.
    assert expected_columns.issubset(actual_columns)


def test_virtual_fitting_user_id_is_foreign_key():
    """
    Verify that virtual_fittings.user_id references users.user_id.
    """

    virtual_fittings_table = Base.metadata.tables["virtual_fittings"]

    user_id_column = virtual_fittings_table.columns["user_id"]

    foreign_keys = list(user_id_column.foreign_keys)

    assert len(foreign_keys) == 1

    assert foreign_keys[0].target_fullname == "users.user_id"    


def test_virtual_fitting_garment_id_is_foreign_key():
    """
    Verify that virtual_fittings.garment_id references
    garments.garment_id.
    """

    virtual_fittings_table = Base.metadata.tables["virtual_fittings"]

    garment_id_column = virtual_fittings_table.columns["garment_id"]

    foreign_keys = list(garment_id_column.foreign_keys)

    assert len(foreign_keys) == 1

    assert foreign_keys[0].target_fullname == "garments.garment_id"    


def test_virtual_fitting_avatar_id_is_foreign_key():
    """
    Verify that virtual_fittings.avatar_id references
    avatars.avatar_id.
    """

    virtual_fittings_table = Base.metadata.tables["virtual_fittings"]

    avatar_id_column = virtual_fittings_table.columns["avatar_id"]

    foreign_keys = list(avatar_id_column.foreign_keys)

    assert len(foreign_keys) == 1

    assert foreign_keys[0].target_fullname == "avatars.avatar_id"
