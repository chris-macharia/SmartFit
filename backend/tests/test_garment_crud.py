"""
Database persistence tests for the SmartFit Garment model.

This module verifies that a Garment can be created and retrieved
using a valid User foreign key.

The test also verifies that the retailer_id field correctly
references the user_id of an existing User.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Garment, User


def test_create_and_retrieve_garment():
    """
    Verify that a Garment can be created and retrieved using
    a valid retailer User foreign key.
    """

    # Create a new database session.
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary retailer User.
        # ---------------------------------------------------------
        #
        # The User must exist before creating the Garment because
        # garments.retailer_id references users.user_id.
        test_user = User(
            full_name="Garment Test Retailer",
            email="garment.test.retailer@smartfit.test",
            hashed_password="test_hashed_password",
            role="retailer",
        )

        # Add the User to the current session.
        db.add(test_user)

        # Commit the User so PostgreSQL generates the UUID.
        db.commit()

        # Refresh the User to retrieve the generated user_id.
        db.refresh(test_user)

        # Confirm that the User received a UUID.
        assert test_user.user_id is not None
        assert isinstance(test_user.user_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 2: Create a temporary Garment.
        # ---------------------------------------------------------
        #
        # The Garment references the actual User UUID.
        test_garment = Garment(
            retailer_id=test_user.user_id,
            name="Test T-Shirt",
            category="T-Shirt",
            brand="SmartFit Test Brand",
            size="M",
            chest=100.0,
            waist=90.0,
            hips=100.0,
            length=70.0,
            image_path="uploads/test_tshirt.jpg",
        )

        # Add the Garment to the session.
        db.add(test_garment)

        # Commit the Garment to PostgreSQL.
        db.commit()

        # Refresh to retrieve generated values.
        db.refresh(test_garment)

        # Confirm that the Garment received a UUID.
        assert test_garment.garment_id is not None
        assert isinstance(test_garment.garment_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 3: Retrieve the Garment.
        # ---------------------------------------------------------

        retrieved_garment = db.query(Garment).filter(
            Garment.garment_id == test_garment.garment_id
        ).first()

        # Confirm that the Garment was retrieved.
        assert retrieved_garment is not None

        # Confirm that the Garment references the correct User.
        assert retrieved_garment.retailer_id == test_user.user_id

        # Verify the Garment data.
        assert retrieved_garment.name == "Test T-Shirt"
        assert retrieved_garment.category == "T-Shirt"
        assert retrieved_garment.brand == "SmartFit Test Brand"
        assert retrieved_garment.size == "M"

        # Confirm that the creation timestamp was generated.
        assert retrieved_garment.created_at is not None

    finally:
        # ---------------------------------------------------------
        # Step 4: Clean up test data.
        # ---------------------------------------------------------
        #
        # Delete the Garment first because it references the User.
        if "test_garment" in locals() and test_garment.garment_id is not None:
            db.delete(test_garment)
            db.commit()

        # Delete the temporary User.
        if "test_user" in locals() and test_user.user_id is not None:
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()