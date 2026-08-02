"""
API tests for SmartFit user authentication.

These tests verify:

1. Successful login with valid credentials.
2. JWT access token generation.
3. Rejection of an incorrect password.
4. Rejection of an unknown email address.

Each test cleans up its database records so the tests
can be executed repeatedly without leftover data.
"""

from jose import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.database import SessionLocal
from app.main import app
from app.models.user import User


# Create a FastAPI test client for making HTTP requests
# against the SmartFit application.
client = TestClient(app)


def delete_user_by_email(email: str):
    """
    Delete a test user from the database using their email address.

    This ensures that authentication tests remain repeatable.
    """

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user:
            db.delete(user)
            db.commit()

    finally:
        db.close()


def create_test_user(email: str, password: str):
    """
    Create a test user through the public registration API.

    Using the registration endpoint ensures that the test user
    receives a properly hashed password, just like a real user.
    """

    response = client.post(
        "/api/users/",
        json={
            "full_name": "Authentication Test User",
            "email": email,
            "password": password,
            "role": "customer",
        },
    )

    assert response.status_code == 201


def test_successful_login_returns_access_token():
    """
    Verify that a registered user can successfully log in
    and receive a JWT access token.
    """

    email = "login.success@example.com"
    password = "SecurePassword123"

    # Remove any leftover test data.
    delete_user_by_email(email)

    try:
        # Create a test account.
        create_test_user(email, password)

        # Attempt to log in.
        response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": password,
            },
        )

        # Login should be successful.
        assert response.status_code == 200

        data = response.json()

        # Verify the response contains an access token.
        assert "access_token" in data
        assert data["access_token"]

        # Verify the token type.
        assert data["token_type"] == "bearer"

    finally:
        # Clean up the test user.
        delete_user_by_email(email)


def test_generated_access_token_contains_user_id():
    """
    Verify that the generated JWT contains the user's UUID
    in the subject (sub) claim.
    """

    email = "login.token@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        # Create a test user.
        create_test_user(email, password)

        # Log in.
        response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        # Decode the JWT using the application's configuration.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # The JWT must contain the subject claim.
        assert "sub" in payload

        # The subject should contain the user's UUID.
        assert payload["sub"]

        # The JWT must contain an expiration claim.
        assert "exp" in payload

    finally:
        delete_user_by_email(email)


def test_login_with_incorrect_password_is_rejected():
    """
    Verify that login fails when the password is incorrect.
    """

    email = "login.incorrect.password@example.com"
    correct_password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        create_test_user(email, correct_password)

        response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": "WrongPassword456",
            },
        )

        assert response.status_code == 401

        assert (
            response.json()["detail"]
            == "Invalid email or password."
        )

    finally:
        delete_user_by_email(email)


def test_login_with_unknown_email_is_rejected():
    """
    Verify that login fails when the email address
    does not belong to a registered user.
    """

    email = "unknown.user@example.com"

    # Make sure this user does not exist.
    delete_user_by_email(email)

    response = client.post(
        "/api/users/login",
        json={
            "email": email,
            "password": "SecurePassword123",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password."
    )