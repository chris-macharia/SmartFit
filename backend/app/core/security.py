"""
Security utilities for the SmartFit backend.

This module contains password hashing and password verification
functions used by the authentication system.

Passwords must never be stored in plain text.

The application follows this flow:

    Plain-text password
            |
            v
      hash_password()
            |
            v
     Password hash
            |
            v
       PostgreSQL

During authentication:

    User enters password
            |
            v
     verify_password()
            |
            v
    True / False
"""

from passlib.context import CryptContext


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


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Args:
        password: The plain-text password supplied by the user.

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
        plain_password: The password entered by the user.
        hashed_password: The password hash retrieved from the database.

    Returns:
        True if the password matches the stored hash.
        False otherwise.
    """

    return pwd_context.verify(
        plain_password,
        hashed_password
    )