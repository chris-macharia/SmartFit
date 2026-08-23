"""
Reusable FastAPI dependencies for the SmartFit backend.

This module contains dependencies that can be shared across
multiple API routes.

The main authentication dependencies are:

- get_current_user():
    Authenticates a request using a JWT bearer token and
    returns the corresponding User object.

- require_retailer():
    Ensures that the authenticated user has the retailer role.
    This is used to protect retailer-only endpoints.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User


# ============================================================
# JWT Bearer Authentication
# ============================================================

# Configure FastAPI's HTTP Bearer authentication scheme.
#
# The client must provide the JWT using:
#
#     Authorization: Bearer <token>
#
security = HTTPBearer()


# ============================================================
# Current User Dependency
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated SmartFit user.

    This dependency:

    1. Extracts the JWT bearer token.
    2. Decodes and validates the JWT.
    3. Extracts the user's UUID from the "sub" claim.
    4. Retrieves the corresponding user from PostgreSQL.
    5. Returns the authenticated User object.

    Args:
        credentials:
            HTTP bearer credentials containing the JWT.

        db:
            Database session provided by get_db().

    Returns:
        User:
            The authenticated SmartFit user.

    Raises:
        HTTPException:
            HTTP 401 Unauthorized if authentication fails.
    """

    # --------------------------------------------------------
    # Extract JWT
    # --------------------------------------------------------

    token = credentials.credentials

    # --------------------------------------------------------
    # Authentication Error
    # --------------------------------------------------------

    # Standard response used whenever authentication fails.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    # --------------------------------------------------------
    # Decode JWT
    # --------------------------------------------------------

    try:
        # Decode and verify the JWT.
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Extract the subject ("sub") claim.
        #
        # The login process stores the user's UUID in this claim.
        user_id = payload.get("sub")

        # A token without a subject cannot identify a user.
        if user_id is None:
            raise credentials_exception

        # Convert the subject from a string into a UUID.
        user_uuid = UUID(user_id)

    except (JWTError, ValueError):
        # JWTError handles invalid, malformed, expired, or
        # incorrectly signed JWTs.
        #
        # ValueError handles invalid UUID values.
        raise credentials_exception

    # --------------------------------------------------------
    # Retrieve User
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.user_id == user_uuid)
        .first()
    )

    # A valid JWT does not guarantee that the user still
    # exists in the database.
    if user is None:
        raise credentials_exception

    # Return the complete authenticated User object.
    #
    # Protected routes can access:
    #
    #     current_user.user_id
    #     current_user.full_name
    #     current_user.email
    #     current_user.role
    return user


# ============================================================
# Retailer Authorization
# ============================================================

def require_retailer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensure that the authenticated user is a retailer.

    This dependency should be used by endpoints that are
    restricted to retailer accounts.

    Authentication and authorization are intentionally separated:

    - get_current_user() verifies who the user is.
    - require_retailer() verifies that the user has permission
      to access retailer-only functionality.

    Args:
        current_user:
            The authenticated SmartFit user.

    Returns:
        User:
            The authenticated retailer.

    Raises:
        HTTPException:
            HTTP 403 Forbidden if the authenticated user is
            not registered as a retailer.
    """

    if current_user.role != "retailer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Retailer access required.",
        )

    return current_user