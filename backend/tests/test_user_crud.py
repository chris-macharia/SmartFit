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

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist user data.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # Create a temporary User object.
        #
        # The password value represents a hashed password.
        # Plain-text passwords should never be stored in the database.
        test_user = User(
            full_name="Test User",
            email="test.user@smartfit.test",
            hashed_password="test_hashed_password",
            role="customer",
        )

        # Add the User object to the current database session.
        db.add(test_user)

        # Commit the transaction so that the user record is
        # written to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves
        # database-generated values such as the UUID and timestamp.
        db.refresh(test_user)

        # Confirm that a user ID was automatically generated.
        assert test_user.id is not None

        # Confirm that the generated user ID is a UUID.
        assert isinstance(test_user.id, uuid.UUID)

        # Retrieve the User record from PostgreSQL using
        # the generated UUID.
        retrieved_user = db.query(User).filter(
            User.id == test_user.id
        ).first()

        # Confirm that the User record was successfully retrieved.
        assert retrieved_user is not None

        # Verify that the retrieved user information matches
        # the information used to create the test record.
        assert retrieved_user.full_name == "Test User"
        assert retrieved_user.email == "test.user@smartfit.test"
        assert retrieved_user.hashed_password == "test_hashed_password"
        assert retrieved_user.role == "customer"

        # Confirm that the account creation timestamp was generated.
        assert retrieved_user.created_at is not None

    finally:
        # Remove the temporary test record from the database.
        #
        # This ensures that running the test does not leave
        # unnecessary test data in the SmartFit database.
        if "test_user" in locals() and test_user.id is not None:
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()