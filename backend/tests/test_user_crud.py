"""
Database CRUD tests for the SmartFit User model.

This module verifies that a User record can be:

1. Created and inserted into PostgreSQL.
2. Retrieved from the database.
3. Deleted after the test completes.

The test uses a temporary test record so that it does not leave
unnecessary data in the development database.
"""

from app.db.database import SessionLocal
from app.models import User


def test_create_and_retrieve_user():
    """
    Verify that a User record can be created and retrieved.

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist a User
    record in PostgreSQL.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # Create a temporary User object.
        #
        # The password is represented by a placeholder hash for
        # testing purposes. Actual password hashing will be
        # implemented when authentication is developed.
        test_user = User(
            full_name="SmartFit Test User",
            email="test.user@smartfit.test",
            hashed_password="temporary_test_hash",
            role="customer",
        )

        # Add the User object to the current database session.
        db.add(test_user)

        # Commit the transaction so that the User is permanently
        # written to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves the
        # database-generated values, such as the user's ID.
        db.refresh(test_user)

        # Confirm that PostgreSQL generated an ID for the new user.
        assert test_user.id is not None

        # Retrieve the User record from PostgreSQL using its ID.
        retrieved_user = db.query(User).filter(
            User.id == test_user.id
        ).first()

        # Confirm that the User record was successfully retrieved.
        assert retrieved_user is not None

        # Verify that the retrieved information matches the
        # information used to create the test User.
        assert retrieved_user.full_name == "SmartFit Test User"
        assert retrieved_user.email == "test.user@smartfit.test"
        assert retrieved_user.role == "customer"

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