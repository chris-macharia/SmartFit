"""
Database persistence tests for the SmartFit User model.

This module verifies that a User record can be:

1. Created and inserted into PostgreSQL.
2. Assigned a UUID primary key.
3. Retrieved from the database.
4. Deleted after the test completes.

The test uses a temporary record so that it does not leave
unnecessary test data in the development database.
"""

import uuid

from app.db.database import SessionLocal
from app.models import User


def test_create_and_retrieve_user():
    """
    Verify that a User record can be created and retrieved
    from PostgreSQL.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # Create a temporary User object.
        test_user = User(
            full_name="Test User",
            email="test.user@smartfit.test",
            hashed_password="test_hashed_password",
            role="customer",
        )

        # Add the User object to the current database session.
        db.add(test_user)

        # Commit the transaction so the user is written to PostgreSQL.
        db.commit()

        # Refresh the object so SQLAlchemy retrieves generated values,
        # including the UUID primary key and creation timestamp.
        db.refresh(test_user)

        # Confirm that a user ID was automatically generated.
        assert test_user.user_id is not None

        # Confirm that the generated user ID is a UUID.
        assert isinstance(test_user.user_id, uuid.UUID)

        # Retrieve the user using the UUID primary key.
        retrieved_user = db.query(User).filter(
            User.user_id == test_user.user_id
        ).first()

        # Confirm that the user was successfully retrieved.
        assert retrieved_user is not None

        # Verify that the retrieved data matches the test data.
        assert retrieved_user.full_name == "Test User"
        assert retrieved_user.email == "test.user@smartfit.test"
        assert retrieved_user.hashed_password == "test_hashed_password"
        assert retrieved_user.role == "customer"

        # Confirm that the creation timestamp was generated.
        assert retrieved_user.created_at is not None

    finally:
        # Remove the temporary test record.
        if "test_user" in locals() and test_user.user_id is not None:
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()