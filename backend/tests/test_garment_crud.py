"""
Database persistence tests for the SmartFit Garment model.

This module verifies that a Garment record can be:

1. Created and inserted into PostgreSQL.
2. Retrieved from the database.
3. Deleted after the test completes.

The test uses a temporary record so that it does not leave
unnecessary test data in the development database.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Garment


def test_create_and_retrieve_garment():
    """
    Verify that a Garment record can be created and retrieved.

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist a Garment
    record in PostgreSQL.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    # Generate a temporary UUID to represent the retailer
    # associated with this test garment.
    #
    # The retailer relationship will be refined later when the
    # User and retailer database design is updated.
    test_retailer_id = uuid.uuid4()

    try:
        # Create a temporary Garment object.
        test_garment = Garment(
            retailer_id=test_retailer_id,
            name="SmartFit Test Shirt",
            category="Shirt",
            brand="SmartFit",
            size="M",
            chest=100.0,
            waist=90.0,
            hips=98.0,
            length=70.0,
            image_path="uploads/test_shirt.jpg",
        )

        # Add the Garment object to the current database session.
        db.add(test_garment)

        # Commit the transaction so that the Garment is written
        # to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves
        # database-generated values such as the garment UUID.
        db.refresh(test_garment)

        # Confirm that PostgreSQL generated a UUID for the garment.
        assert test_garment.garment_id is not None

        # Retrieve the Garment record from PostgreSQL using
        # the generated garment UUID.
        retrieved_garment = db.query(Garment).filter(
            Garment.garment_id == test_garment.garment_id
        ).first()

        # Confirm that the Garment record was successfully retrieved.
        assert retrieved_garment is not None

        # Verify that the retrieved information matches the
        # information used to create the test Garment.
        assert retrieved_garment.retailer_id == test_retailer_id
        assert retrieved_garment.name == "SmartFit Test Shirt"
        assert retrieved_garment.category == "Shirt"
        assert retrieved_garment.brand == "SmartFit"
        assert retrieved_garment.size == "M"
        assert retrieved_garment.chest == 100.0
        assert retrieved_garment.waist == 90.0
        assert retrieved_garment.hips == 98.0
        assert retrieved_garment.length == 70.0
        assert retrieved_garment.image_path == "uploads/test_shirt.jpg"

    finally:
        # Remove the temporary test record from the database.
        #
        # This ensures that running the test does not leave
        # unnecessary test data in the SmartFit database.
        if (
            "test_garment" in locals()
            and test_garment.garment_id is not None
        ):
            db.delete(test_garment)
            db.commit()

        # Close the database session.
        db.close()