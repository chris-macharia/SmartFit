"""
Pydantic schemas for the SmartFit User API.

This module defines the data structures used when receiving
user data from API requests and returning user data in API responses.

Pydantic schemas are separate from SQLAlchemy database models:

- SQLAlchemy models define how data is stored in PostgreSQL.
- Pydantic schemas define how data enters and leaves the API.
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """
    Schema used when creating a new SmartFit user.

    This schema defines the data that the API expects from
    the client when registering a new user.

    The password is received as plain text at the API boundary.
    It must be securely hashed before being stored in the database.
    """

    full_name: str
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    """
    Schema used when a user attempts to log in.

    The user provides their registered email address and
    plain-text password. The password is verified against
    the securely stored password hash.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Schema returned after successful user authentication.

    The access_token is a signed JWT that the client can use
    to authenticate subsequent requests.

    token_type identifies the authentication scheme used by
    the client when sending the token in the Authorization header.
    """

    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """
    Schema used when returning a user through the API.

    Sensitive information such as the user's hashed password
    is deliberately excluded from API responses.

    The user's UUID is returned so that the client can identify
    the created user.
    """

    user_id: UUID
    full_name: str
    email: EmailStr
    role: str

    # Allows Pydantic to read data directly from SQLAlchemy
    # model instances when generating API responses.
    model_config = ConfigDict(from_attributes=True)