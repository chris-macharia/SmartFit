"""
Database persistence tests for the SmartFit Avatar model.

This module verifies that an Avatar record can be:

1. Created and inserted into PostgreSQL.
2. Retrieved from the database.
3. Deleted after the test completes.

The test uses a temporary record so that it does not leave
unnecessary test data in the development database.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Avatar


def test_create_and_retrieve_avatar():
    """
    Verify that an Avatar record can be created and retrieved
    from PostgreSQL.

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist an Avatar
    record in the SmartFit database.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    # Generate a temporary UUID to represent the body measurement
    # record associated with this test avatar.
    #
    # The relationship between Avatar and BodyMeasurement will be
    # refined later when the database relationships are finalized.
    test_measurement_id = uuid.uuid4()

    try:
        # Create a temporary Avatar object.
        #
        # The avatar_path represents the location where the generated
        # avatar file would be stored by the SmartFit application.
        test_avatar = Avatar(
            measurement_id=test_measurement_id,
            avatar_path="uploads/test_avatar.glb",
        )

        # Add the Avatar object to the current database session.
        db.add(test_avatar)

        # Commit the transaction so that the Avatar record is
        # written to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves
        # database-generated values such as the avatar UUID
        # and creation timestamp.
        db.refresh(test_avatar)

        # Confirm that PostgreSQL generated a UUID for the avatar.
        assert test_avatar.avatar_id is not None

        # Retrieve the Avatar record from PostgreSQL using
        # the generated avatar UUID.
        retrieved_avatar = db.query(Avatar).filter(
            Avatar.avatar_id == test_avatar.avatar_id
        ).first()

        # Confirm that the Avatar record was successfully retrieved.
        assert retrieved_avatar is not None

        # Verify that the retrieved measurement ID matches
        # the ID used to create the test avatar.
        assert retrieved_avatar.measurement_id == test_measurement_id

        # Verify that the avatar file path was correctly stored
        # and retrieved from PostgreSQL.
        assert retrieved_avatar.avatar_path == "uploads/test_avatar.glb"

        # Confirm that the creation timestamp was automatically
        # generated when the Avatar record was created.
        assert retrieved_avatar.created_at is not None

    finally:
        # Remove the temporary test record from the database.
        #
        # This ensures that running the test does not leave
        # unnecessary test data in the SmartFit database.
        if (
            "test_avatar" in locals()
            and test_avatar.avatar_id is not None
        ):
            db.delete(test_avatar)
            db.commit()

        # Close the database session.
        db.close()