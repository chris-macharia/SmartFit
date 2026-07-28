"""
API tests for SmartFit user registration.

These tests verify the complete user registration flow through
the HTTP API, including:

1. Successful user registration.
2. Password hashing before database storage.
3. Password hash exclusion from API responses.
4. Duplicate email rejection.
5. Invalid email validation.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.user import User


# Create a FastAPI test client for making HTTP requests
# against the application.
client = TestClient(app)


def test_create_user():
    """
    Verify that a valid user can be registered successfully.
    """

    response = client.post(
        "/api/users/",
        json={
            "full_name": "Test User",
            "email": "test.user@example.com",
            "password": "SecurePassword123",
            "role": "customer",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test User"
    assert data["email"] == "test.user@example.com"
    assert data["role"] == "customer"

    # The API response must contain the generated UUID.
    assert "user_id" in data

    # Password information must never be returned.
    assert "password" not in data
    assert "hashed_password" not in data


def test_password_is_hashed_in_database():
    """
    Verify that the user's plain-text password is never stored
    directly in the database.
    """

    email = "hashed.password@example.com"
    password = "SecurePassword123"

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
        db.close()


def test_duplicate_email_is_rejected():
    """
    Verify that registering an email that already exists
    returns HTTP 409 Conflict.
    """

    email = "duplicate@example.com"

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