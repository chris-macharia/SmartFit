"""
Tests for the SmartFit JWT authentication dependency.

These tests verify that get_current_user():

1. Accepts a valid JWT and returns the correct user.
2. Rejects an invalid JWT.
3. Rejects a JWT without a subject claim.
4. Rejects a JWT containing an invalid UUID.
5. Rejects a valid token belonging to a non-existent user.
6. Rejects an expired JWT.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import SessionLocal
from app.models.user import User


def delete_user_by_email(email: str):
    """
    Delete a test user from the database.

    This keeps the tests repeatable by ensuring that test data
    from previous runs does not remain in the test database.
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


def create_test_user(email: str) -> User:
    """
    Create a temporary test user directly in the database.

    The password hash is not relevant to these tests because
    the tests focus specifically on JWT authentication.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Authentication Dependency User",
            email=email,
            hashed_password="test_hashed_password",
            role="customer",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def test_get_current_user_returns_authenticated_user():
    """
    Verify that a valid JWT returns the correct User object.
    """

    email = "dependency.valid@example.com"

    delete_user_by_email(email)

    user = create_test_user(email)

    db = SessionLocal()

    try:
        # Create a valid JWT containing the user's UUID.
        token = create_access_token(
            data={
                "sub": str(user.user_id),
            }
        )

        # Run the authentication dependency directly.
        authenticated_user = get_current_user(
            token=token,
            db=db,
        )

        # Verify that the correct user was returned.
        assert authenticated_user is not None
        assert authenticated_user.user_id == user.user_id
        assert authenticated_user.email == email

    finally:
        db.close()
        delete_user_by_email(email)


def test_invalid_token_is_rejected():
    """
    Verify that a malformed or invalid JWT is rejected.
    """

    db = SessionLocal()

    try:
        invalid_token = "this.is.not.a.valid.jwt"

        try:
            get_current_user(
                token=invalid_token,
                db=db,
            )

            # The function should never successfully return
            # when an invalid token is supplied.
            assert False

        except Exception as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Could not validate authentication credentials."
            )

    finally:
        db.close()


def test_token_without_subject_is_rejected():
    """
    Verify that a JWT without a "sub" claim is rejected.
    """

    db = SessionLocal()

    try:
        # Create a token without the required subject claim.
        token = jwt.encode(
            {
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        try:
            get_current_user(
                token=token,
                db=db,
            )

            assert False

        except Exception as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Could not validate authentication credentials."
            )

    finally:
        db.close()


def test_token_with_invalid_uuid_is_rejected():
    """
    Verify that a JWT containing an invalid UUID is rejected.
    """

    db = SessionLocal()

    try:
        # Create a validly signed JWT, but use an invalid UUID
        # as the subject.
        token = create_access_token(
            data={
                "sub": "not-a-valid-uuid",
            }
        )

        try:
            get_current_user(
                token=token,
                db=db,
            )

            assert False

        except Exception as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Could not validate authentication credentials."
            )

    finally:
        db.close()


def test_token_for_nonexistent_user_is_rejected():
    """
    Verify that a valid JWT is rejected if the referenced
    user does not exist in the database.
    """

    db = SessionLocal()

    try:
        # Generate a valid UUID that does not belong to a user.
        import uuid

        token = create_access_token(
            data={
                "sub": str(uuid.uuid4()),
            }
        )

        try:
            get_current_user(
                token=token,
                db=db,
            )

            assert False

        except Exception as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Could not validate authentication credentials."
            )

    finally:
        db.close()


def test_expired_token_is_rejected():
    """
    Verify that an expired JWT cannot authenticate a user.
    """

    email = "dependency.expired@example.com"

    delete_user_by_email(email)

    user = create_test_user(email)

    db = SessionLocal()

    try:
        # Create a token that expired one minute ago.
        token = jwt.encode(
            {
                "sub": str(user.user_id),
                "exp": datetime.now(timezone.utc)
                - timedelta(minutes=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        try:
            get_current_user(
                token=token,
                db=db,
            )

            assert False

        except Exception as exc:
            assert exc.status_code == 401
            assert (
                exc.detail
                == "Could not validate authentication credentials."
            )

    finally:
        db.close()
        delete_user_by_email(email)