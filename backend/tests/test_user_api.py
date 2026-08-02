"""
API tests for SmartFit user registration and authentication.

These tests verify the complete user API flow, including:

1. Successful user registration.
2. Password hashing before database storage.
3. Password hash exclusion from API responses.
4. Duplicate email rejection.
5. Invalid email validation.
6. Authenticated user profile retrieval.
7. Authentication requirement for protected endpoints.
8. Rejection of invalid JWT access tokens.

The tests use the isolated SmartFit_Test_db database.

Tests that create users clean up their test data so that the
test suite can be executed repeatedly without leftover records
causing duplicate email conflicts.
"""

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.models.user import User


# Create a FastAPI test client for making HTTP requests
# against the SmartFit application.
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
        # Send a registration request to the API.
        response = client.post(
            "/api/users/",
            json={
                "full_name": "Test User",
                "email": email,
                "password": "SecurePassword123",
                "role": "customer",
            },
        )

        # Registration should return HTTP 201 Created.
        assert response.status_code == 201

        # Extract the response data.
        data = response.json()

        # Verify that the returned user information is correct.
        assert data["full_name"] == "Test User"
        assert data["email"] == email
        assert data["role"] == "customer"

        # The API response must contain the generated UUID.
        assert "user_id" in data

        # Password information must never be returned
        # by the API.
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
        # Register a new user through the API.
        response = client.post(
            "/api/users/",
            json={
                "full_name": "Hashed Password User",
                "email": email,
                "password": password,
                "role": "customer",
            },
        )

        # Registration should succeed.
        assert response.status_code == 201

        # Open a database session to inspect the stored user.
        db = SessionLocal()

        try:
            # Retrieve the newly created user.
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

            # Confirm that the user exists.
            assert user is not None

            # The stored password must not equal the
            # original plain-text password.
            assert user.hashed_password != password

            # The stored password hash must not be empty.
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

        # The first registration should succeed.
        assert first_response.status_code == 201

        # Attempt to register another user using
        # the same email address.
        second_response = client.post(
            "/api/users/",
            json={
                "full_name": "Second User",
                "email": email,
                "password": "AnotherPassword456",
                "role": "customer",
            },
        )

        # The duplicate registration should be rejected.
        assert second_response.status_code == 409

        # Verify the error message returned by the API.
        assert (
            second_response.json()["detail"]
            == "A user with this email already exists."
        )

    finally:
        # Remove the test user created during the test.
        delete_user_by_email(email)


def test_invalid_email_is_rejected():
    """
    Verify that an invalid email address is rejected
    by the Pydantic UserCreate schema.
    """

    # Send a registration request containing an invalid email.
    response = client.post(
        "/api/users/",
        json={
            "full_name": "Invalid Email User",
            "email": "not-a-valid-email",
            "password": "SecurePassword123",
            "role": "customer",
        },
    )

    # FastAPI should return HTTP 422 Unprocessable Entity.
    assert response.status_code == 422


def test_get_current_user_profile():
    """
    Verify that an authenticated user can retrieve their own profile.

    The test verifies the complete authentication flow:

    1. Register a user.
    2. Log in using the user's email and password.
    3. Receive a JWT access token.
    4. Use the token to access the protected profile endpoint.
    5. Verify that the correct user profile is returned.
    6. Verify that sensitive password information is not exposed.

    The test user is deleted before and after the test to ensure
    that the test can be executed repeatedly without duplicate
    email conflicts.
    """

    email = "profile.user@example.com"
    password = "SecurePassword123"

    # Make sure the test starts with a clean database state.
    #
    # This prevents a previous failed test run from causing
    # the registration request to return HTTP 409 Conflict.
    delete_user_by_email(email)

    try:
        # ========================================================
        # Step 1: Register a new user.
        # ========================================================

        register_response = client.post(
            "/api/users/",
            json={
                "full_name": "Profile User",
                "email": email,
                "password": password,
                "role": "customer",
            },
        )

        # Registration should succeed.
        assert register_response.status_code == 201

        # ========================================================
        # Step 2: Log in to obtain a JWT access token.
        # ========================================================

        # The login endpoint expects JSON containing the
        # user's email address and plain-text password.
        login_response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": password,
            },
        )

        # Login should succeed.
        assert login_response.status_code == 200

        # Extract the JWT access token from the response.
        token = login_response.json()["access_token"]

        # Verify that an access token was returned.
        assert token

        # ========================================================
        # Step 3: Access the protected profile endpoint.
        # ========================================================

        # Send the JWT using the standard Bearer authentication
        # format in the Authorization header.
        profile_response = client.get(
            "/api/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        # The authenticated request should succeed.
        assert profile_response.status_code == 200

        # Extract the returned user profile.
        data = profile_response.json()

        # ========================================================
        # Step 4: Verify the returned user information.
        # ========================================================

        assert data["full_name"] == "Profile User"
        assert data["email"] == email
        assert data["role"] == "customer"

        # The API response must contain the user's UUID.
        assert "user_id" in data

        # ========================================================
        # Step 5: Verify sensitive information is protected.
        # ========================================================

        # The plain-text password must never be returned.
        assert "password" not in data

        # The password hash must also never be returned.
        assert "hashed_password" not in data

    finally:
        # Remove the test user after the test completes.
        #
        # This ensures that the test does not leave data behind
        # and can be safely executed again.
        delete_user_by_email(email)


def test_get_current_user_profile_requires_authentication():
    """
    Verify that the profile endpoint rejects requests
    without a JWT access token.
    """

    # Attempt to access the protected endpoint without
    # providing an Authorization header.
    response = client.get(
        "/api/users/me"
    )

    # The request should be rejected with HTTP 401 Unauthorized.
    assert response.status_code == 401


def test_get_current_user_profile_rejects_invalid_token():
    """
    Verify that the profile endpoint rejects an invalid JWT.
    """

    # Attempt to access the protected endpoint using
    # an invalid JWT access token.
    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": "Bearer invalid.token.here",
        },
    )

    # The request should be rejected with HTTP 401 Unauthorized.
    assert response.status_code == 401