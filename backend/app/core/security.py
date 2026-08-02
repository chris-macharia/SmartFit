"""
Security utilities for the SmartFit backend.

This module contains security-related functions used by the
authentication system.

The module is responsible for:

1. Password hashing.
2. Password verification.
3. JWT access token creation.

Passwords must never be stored in plain text.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# ============================================================
# Password Hashing Configuration
# ============================================================

# Configure the password hashing context.
#
# bcrypt is used as the password hashing algorithm.
# The deprecated="auto" setting allows Passlib to identify
# older hashing schemes automatically if the application
# later needs to support password hash migrations.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# Password Functions
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Args:
        password:
            The plain-text password supplied by the user.

    Returns:
        A securely hashed password suitable for database storage.
    """

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against a stored password hash.

    Args:
        plain_password:
            The password entered by the user.

        hashed_password:
            The password hash retrieved from the database.

    Returns:
        True if the password matches the stored hash.
        False otherwise.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# JWT Functions
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create a signed JWT access token.

    Args:
        data:
            Data to include in the JWT payload.

        expires_delta:
            Optional custom token expiration period.

    Returns:
        A signed JWT access token.
    """

    # Copy the payload so that the original dictionary
    # supplied by the caller is not modified.
    to_encode = data.copy()

    # Determine the token expiration time.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )

    # Add the expiration time to the JWT payload.
    to_encode.update(
        {
            "exp": expire,
        }
    )

    # Create and return the signed JWT token.
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt