"""
API tests for SmartFit user registration.

These tests verify the complete user registration flow through
the HTTP API, including:

1. Successful user registration.
2. Password hashing before database storage.
3. Password hash exclusion from API responses.
4. Duplicate email rejection.
5. Invalid email validation.

The tests use the isolated SmartFit_Test_db database and clean up
any users created during each test so that the test suite can be
run repeatedly without leftover test data causing failures.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.user import User


# Create a FastAPI test client for making HTTP requests
# against the application.
client = TestClient(app)


def delete_user_by_email(email: str):
    """
    Delete a test user from the database using their email address.

    This helper is used to clean up users created during API tests.
    Keeping test data cleanup in one place makes the tests easier
    to maintain and ensures that repeated test runs do not fail
    because of leftover records.
    """

    # Create a database session.
    db = SessionLocal()

    try:
        # Find the user created by the test.
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        # Delete the user if they exist.
        if user:
            db.delete(user)
            db.commit()

    finally:
        # Always close the database session.
        db.close()


def test_create_user():
    """
    Verify that a valid user can be registered successfully.
    """

    email = "test.user@example.com"

    # Make sure the test starts with a clean database state.
    delete_user_by_email(email)

    try:
        response = client.post(
            "/api/users/",
            json={
                "full_name": "Test User",
                "email": email,
                "password": "SecurePassword123",
                "role": "customer",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["full_name"] == "Test User"
        assert data["email"] == email
        assert data["role"] == "customer"

        # The API response must contain the generated UUID.
        assert "user_id" in data

        # Password information must never be returned.
        assert "password" not in data
        assert "hashed_password" not in data

    finally:
        # Remove the test user so the test can be run repeatedly.
        delete_user_by_email(email)


def test_password_is_hashed_in_database():
    """
    Verify that the user's plain-text password is never stored
    directly in the database.
    """

    email = "hashed.password@example.com"
    password = "SecurePassword123"

    # Make sure the test starts with a clean database state.
    delete_user_by_email(email)

    try:
        response = client.post(
            "/api/users/",
            json={
                "full_name": "Hashed Password User",
                "email": email,
                "password": password,
                "role": "customer",
            },
        )

        assert response.status_code == 201

        # Open a database session to inspect the stored user.
        db = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            assert user is not None

            # The stored password must not equal the original password.
            assert user.hashed_password != password

            # The stored value should be a non-empty password hash.
            assert user.hashed_password

        finally:
            # Close the database session used for verification.
            db.close()

    finally:
        # Remove the test user so the test can be run repeatedly.
        delete_user_by_email(email)


def test_duplicate_email_is_rejected():
    """
    Verify that registering an email that already exists
    returns HTTP 409 Conflict.
    """

    email = "duplicate@example.com"

    # Make sure the test starts with a clean database state.
    delete_user_by_email(email)

    try:
        # Register the first user.
        first_response = client.post(
            "/api/users/",
            json={
                "full_name": "First User",
                "email": email,
                "password": "SecurePassword123",
                "role": "customer",
            },
        )

        assert first_response.status_code == 201

        # Attempt to register another user with the same email.
        second_response = client.post(
            "/api/users/",
            json={
                "full_name": "Second User",
                "email": email,
                "password": "AnotherPassword456",
                "role": "customer",
            },
        )

        assert second_response.status_code == 409

        assert (
            second_response.json()["detail"]
            == "A user with this email already exists."
        )

    finally:
        # Remove the first user created during the test.
        delete_user_by_email(email)


def test_invalid_email_is_rejected():
    """
    Verify that an invalid email address is rejected
    by the Pydantic UserCreate schema.
    """

    response = client.post(
        "/api/users/",
        json={
            "full_name": "Invalid Email User",
            "email": "not-a-valid-email",
            "password": "SecurePassword123",
            "role": "customer",
        },
    )

    assert response.status_code == 422