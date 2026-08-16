"""
Authentication dependencies for SmartFit.

This module contains reusable FastAPI dependencies used to
authenticate users through JWT access tokens.

The main dependency, get_current_user(), extracts the user ID
from a JWT, validates the token, and retrieves the corresponding
User record from the database.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


# OAuth2PasswordBearer tells FastAPI where clients should obtain
# their access token.
#
# The tokenUrl must match the login endpoint exposed by SmartFit.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate the current user using a JWT access token.

    The function performs the following steps:

    1. Decode and validate the JWT.
    2. Extract the user's UUID from the "sub" claim.
    3. Validate that the UUID is correctly formatted.
    4. Retrieve the user from the database.
    5. Return the authenticated User object.

    Any authentication failure returns HTTP 401 with the same
    generic error message. This avoids exposing unnecessary
    information about why authentication failed.
    """

    # Use one consistent authentication error message for all
    # token and user-validation failures.
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        # Decode the JWT using the application's configured
        # secret key and signing algorithm.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Extract the subject ("sub") claim.
        #
        # SmartFit stores the user's UUID as the JWT subject.
        user_id = payload.get("sub")

        # A token without a subject cannot identify a user.
        if user_id is None:
            raise authentication_error

        # Convert the subject into a UUID.
        #
        # This also validates that the JWT contains a properly
        # formatted SmartFit user UUID.
        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, AttributeError, TypeError):
            raise authentication_error

    except JWTError:
        # This handles malformed, invalidly signed, or expired
        # JWTs.
        raise authentication_error

    # Retrieve the user represented by the JWT.
    user = (
        db.query(User)
        .filter(User.user_id == user_uuid)
        .first()
    )

    # Do not reveal whether the user exists or not.
    # Treat a nonexistent user as an invalid authentication
    # credential.
    if user is None:
        raise authentication_error

    # Authentication succeeded.
    return user