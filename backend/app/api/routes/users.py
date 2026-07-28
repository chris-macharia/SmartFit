"""
User API routes for the SmartFit backend.

This module contains API endpoints related to SmartFit users.

The user registration endpoint is responsible for:

1. Validating incoming user data using Pydantic.
2. Checking whether the email is already registered.
3. Hashing the user's password.
4. Creating a new User database record.
5. Returning safe user information without exposing the password hash.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


# Create a router specifically for user-related endpoints.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_db():
    """
    Provide a database session to API endpoints.

    A new SQLAlchemy session is created for each request.
    The session is automatically closed after the request
    has been completed.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


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
        UserResponse: Safe user information without the password.
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