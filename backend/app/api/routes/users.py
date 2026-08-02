"""
User API routes for the SmartFit backend.

This module contains API endpoints related to SmartFit users.

The available endpoints are responsible for:

1. Registering new users.
2. Hashing passwords before database storage.
3. Authenticating existing users.
4. Generating JWT access tokens after successful login.
5. Returning safe user information without exposing password hashes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)


# Create a router specifically for user-related endpoints.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new SmartFit user.

    The user's plain-text password is hashed before the User
    record is stored in PostgreSQL.

    Returns:
        UserResponse:
            Safe user information without the password.
    """

    # Check whether another account already uses this email.
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # Hash the plain-text password before storing the user.
    hashed_password = hash_password(user_data.password)

    # Create a new SQLAlchemy User object.
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
    )

    # Add the new user to the current database session.
    db.add(new_user)

    # Commit the transaction so the user is permanently
    # saved in the PostgreSQL database.
    db.commit()

    # Refresh the object so automatically generated fields
    # such as user_id and created_at are available.
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a SmartFit user and return a JWT access token.

    The user is identified using their email address. The supplied
    password is verified against the securely stored password hash.

    Returns:
        TokenResponse:
            A signed JWT access token and its token type.

    Raises:
        HTTPException:
            HTTP 401 Unauthorized when the email does not exist
            or the supplied password is incorrect.
    """

    # Find the user using the supplied email address.
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    # Reject the login if no account exists with this email.
    #
    # We intentionally use the same error message for an unknown
    # email and an incorrect password. This prevents attackers
    # from determining which email addresses are registered.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Verify the supplied plain-text password against
    # the password hash stored in the database.
    password_is_valid = verify_password(
        user_data.password,
        user.hashed_password,
    )

    # Reject the login if the password does not match.
    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Create a JWT access token.
    #
    # The user's UUID is stored in the "sub" (subject) claim.
    # The UUID is converted to a string because JWT payloads
    # must contain JSON-compatible values.
    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )

    # Return the access token to the client.
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }