"""
Reusable FastAPI dependencies for the SmartFit backend.

This module contains dependencies that can be shared across
multiple API routes.

The main authentication dependency is get_current_user(),
which:

1. Extracts the JWT bearer token from the request.
2. Decodes and validates the JWT.
3. Retrieves the user's UUID from the "sub" claim.
4. Finds the corresponding user in the database.
5. Returns the authenticated User object.

Routes can use this dependency to ensure that only authenticated
users can access protected resources.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


# ============================================================
# JWT Bearer Authentication
# ============================================================

# Configure FastAPI's OAuth2 bearer token security scheme.
#
# The tokenUrl identifies the endpoint where users authenticate.
# This is also used by FastAPI's automatically generated
# Swagger/OpenAPI documentation.
#
# The endpoint currently used for login is:
#
#     POST /api/users/login
#
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/users/login"
)


# ============================================================
# Current User Dependency
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated SmartFit user.

    This dependency is used by protected API endpoints.

    The process is:

    1. FastAPI extracts the bearer token from the Authorization header.
    2. The JWT signature and expiration are validated.
    3. The user's UUID is extracted from the "sub" claim.
    4. The user is retrieved from PostgreSQL.
    5. The authenticated User object is returned.

    Args:
        token:
            JWT access token extracted from the Authorization header.

        db:
            Database session provided by the get_db dependency.

    Returns:
        User:
            The authenticated SmartFit user.

    Raises:
        HTTPException:
            HTTP 401 Unauthorized if the token is invalid,
            malformed, expired, or belongs to a user that
            no longer exists.
    """

    # Define the standard response used when authentication fails.
    #
    # The WWW-Authenticate header tells the client that the
    # endpoint requires bearer token authentication.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        # Decode and verify the JWT.
        #
        # The SECRET_KEY verifies that the token was created
        # by our application.
        #
        # The ALGORITHM specifies which signing algorithm
        # should be used to validate the token.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Extract the subject ("sub") claim from the JWT.
        #
        # Our login endpoint stores the user's UUID in this claim.
        user_id = payload.get("sub")

        # A JWT without a subject cannot be used to identify
        # the authenticated SmartFit user.
        if user_id is None:
            raise credentials_exception

        # Convert the subject string back into a UUID.
        #
        # This also validates that the value stored in the JWT
        # is a correctly formatted UUID.
        user_uuid = UUID(user_id)

    except (JWTError, ValueError):
        # JWTError catches invalid signatures, expired tokens,
        # malformed tokens, and other JWT-related errors.
        #
        # ValueError catches invalid UUID values.
        raise credentials_exception

    # Retrieve the user associated with the UUID from PostgreSQL.
    user = (
        db.query(User)
        .filter(User.user_id == user_uuid)
        .first()
    )

    # The token may be valid, but the user could have been
    # deleted from the database after the token was issued.
    if user is None:
        raise credentials_exception

    # Return the authenticated User object.
    #
    # The protected route can now access information such as:
    #
    #     current_user.user_id
    #     current_user.email
    #     current_user.full_name
    #     current_user.role
    return user