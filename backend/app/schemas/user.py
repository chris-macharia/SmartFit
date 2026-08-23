"""
Pydantic schemas for the SmartFit User API.

This module defines the data structures used when receiving
user data from API requests and returning user data in API responses.

Pydantic schemas are separate from SQLAlchemy database models:

- SQLAlchemy models define how data is stored in PostgreSQL.
- Pydantic schemas define how data enters and leaves the API.
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# ============================================================
# User Creation
# ============================================================

class UserCreate(BaseModel):
    """
    Schema used when creating a new SmartFit user.

    A SmartFit account can currently have one of two roles:

    - customer
    - retailer

    The password is received as plain text at the API boundary
    and must be securely hashed before being stored.
    """

    full_name: str
    email: EmailStr
    password: str
    role: Literal["customer", "retailer"]


# ============================================================
# User Login
# ============================================================

class UserLogin(BaseModel):
    """
    Schema used when a user attempts to log in.

    The user provides their registered email address and
    plain-text password.
    """

    email: EmailStr
    password: str


# ============================================================
# Authentication Response
# ============================================================

class TokenResponse(BaseModel):
    """
    Schema returned after successful user authentication.

    The access_token is a signed JWT that the client uses
    to authenticate subsequent requests.

    token_type identifies the authentication scheme used
    in the Authorization header.
    """

    access_token: str
    token_type: str


# ============================================================
# User Response
# ============================================================

class UserResponse(BaseModel):
    """
    Schema used when returning a user through the API.

    Sensitive information such as the hashed password is
    deliberately excluded from API responses.
    """

    user_id: UUID
    full_name: str
    email: EmailStr
    role: Literal["customer", "retailer"]

    # Allows Pydantic to read data directly from SQLAlchemy
    # model instances.
    model_config = ConfigDict(from_attributes=True)