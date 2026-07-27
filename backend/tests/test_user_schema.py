"""
Tests for SmartFit User Pydantic schemas.

These tests verify that:

1. Valid user data can be accepted by UserCreate.
2. Invalid email addresses are rejected.
3. UserResponse contains only safe user information.
4. UserResponse does not expose the user's hashed password.
"""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse


def test_user_create_accepts_valid_data():
    """
    Verify that UserCreate accepts valid user registration data.
    """

    user = UserCreate(
        full_name="John Doe",
        email="john@example.com",
        password="SecurePassword123",
        role="customer"
    )

    assert user.full_name == "John Doe"
    assert user.email == "john@example.com"
    assert user.password == "SecurePassword123"
    assert user.role == "customer"


def test_user_create_rejects_invalid_email():
    """
    Verify that UserCreate rejects an invalid email address.

    Pydantic's EmailStr type should raise a ValidationError
    when the supplied email does not have a valid format.
    """

    with pytest.raises(ValidationError):
        UserCreate(
            full_name="John Doe",
            email="not-a-valid-email",
            password="SecurePassword123",
            role="customer"
        )


def test_user_response_contains_safe_user_information():
    """
    Verify that UserResponse contains the fields that are safe
    to expose through the API.
    """

    user_id = uuid4()

    user = UserResponse(
        user_id=user_id,
        full_name="John Doe",
        email="john@example.com",
        role="customer"
    )

    assert user.user_id == user_id
    assert user.full_name == "John Doe"
    assert user.email == "john@example.com"
    assert user.role == "customer"


def test_user_response_does_not_expose_hashed_password():
    """
    Verify that the API response schema does not contain
    a hashed password field.

    Password hashes must never be returned to API clients.
    """

    user_id = uuid4()

    user = UserResponse(
        user_id=user_id,
        full_name="John Doe",
        email="john@example.com",
        role="customer"
    )

    response_data = user.model_dump()

    assert "hashed_password" not in response_data
    assert "password" not in response_data