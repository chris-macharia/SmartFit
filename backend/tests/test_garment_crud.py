"""
Database persistence tests for the SmartFit Garment model.

This module verifies that a Garment can be created and retrieved
using a valid User foreign key.

The User must have the retailer role because garments are
registered by retailers.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Garment, User


def test_create_and_retrieve_garment():
    """
    Verify that a Garment can be created and retrieved using
    a valid retailer User foreign key.
    """

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary retailer User.
        # ---------------------------------------------------------

        test_user = User(
            full_name="Garment Test Retailer",
            email="garment.test.retailer@smartfit.test",
            hashed_password="test_hashed_password",
            role="retailer",
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        # Confirm that the User received a UUID.
        assert test_user.user_id is not None
        assert isinstance(test_user.user_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 2: Create a temporary Garment.
        # ---------------------------------------------------------

        test_garment = Garment(
            user_id=test_user.user_id,
            chest_width=100.0,
            waist_width=90.0,
            hip_width=100.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        db.add(test_garment)
        db.commit()
        db.refresh(test_garment)

        # Confirm that the Garment received a UUID.
        assert test_garment.garment_id is not None
        assert isinstance(
            test_garment.garment_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 3: Retrieve the Garment.
        # ---------------------------------------------------------

        retrieved_garment = (
            db.query(Garment)
            .filter(
                Garment.garment_id
                == test_garment.garment_id
            )
            .first()
        )

        # Confirm that the Garment was retrieved.
        assert retrieved_garment is not None

        # Confirm that the Garment references the
        # correct retailer User.
        assert (
            retrieved_garment.user_id
            == test_user.user_id
        )

        # ---------------------------------------------------------
        # Step 4: Verify garment measurements.
        # ---------------------------------------------------------

        assert float(
            retrieved_garment.chest_width
        ) == 100.0

        assert float(
            retrieved_garment.waist_width
        ) == 90.0

        assert float(
            retrieved_garment.hip_width
        ) == 100.0

        assert float(
            retrieved_garment.shoulder_width
        ) == 45.0

        assert float(
            retrieved_garment.inseam
        ) == 80.0

        # Confirm that the creation timestamp was generated.
        assert retrieved_garment.created_at is not None

    finally:
        # ---------------------------------------------------------
        # Step 5: Clean up test data.
        # ---------------------------------------------------------

        # Delete the Garment first because it references the User.
        if (
            "test_garment" in locals()
            and test_garment.garment_id is not None
        ):
            db.delete(test_garment)
            db.commit()

        # Delete the temporary User.
        if (
            "test_user" in locals()
            and test_user.user_id is not None
        ):
            db.delete(test_user)
            db.commit()

        db.close()