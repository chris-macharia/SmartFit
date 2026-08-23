"""
Pydantic schemas for the SmartFit Garment API.

This module defines the data structures used when receiving
garment data from API requests and returning garment data
in API responses.

The schemas are separate from the SQLAlchemy Garment model:

- SQLAlchemy defines how garment data is stored in PostgreSQL.
- Pydantic defines how garment data enters and leaves the API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Garment Creation
# ============================================================

class GarmentCreate(BaseModel):
    """
    Schema used when creating a new garment.

    The uploader's user_id is intentionally excluded.

    The authenticated user's ID is obtained from the JWT by
    the API and assigned by the backend.
    """

    chest_width: float = Field(
        ...,
        gt=0,
        description="Garment chest width in centimetres.",
    )

    waist_width: float = Field(
        ...,
        gt=0,
        description="Garment waist width in centimetres.",
    )

    hip_width: float = Field(
        ...,
        gt=0,
        description="Garment hip width in centimetres.",
    )

    shoulder_width: float = Field(
        ...,
        gt=0,
        description="Garment shoulder width in centimetres.",
    )

    inseam: float = Field(
        ...,
        gt=0,
        description="Garment inseam length in centimetres.",
    )


# ============================================================
# Garment Update
# ============================================================

class GarmentUpdate(BaseModel):
    """
    Schema used when updating an existing garment.

    All fields are optional so that individual measurements
    can be updated without requiring the complete garment.
    """

    chest_width: float | None = Field(
        default=None,
        gt=0,
        description="Garment chest width in centimetres.",
    )

    waist_width: float | None = Field(
        default=None,
        gt=0,
        description="Garment waist width in centimetres.",
    )

    hip_width: float | None = Field(
        default=None,
        gt=0,
        description="Garment hip width in centimetres.",
    )

    shoulder_width: float | None = Field(
        default=None,
        gt=0,
        description="Garment shoulder width in centimetres.",
    )

    inseam: float | None = Field(
        default=None,
        gt=0,
        description="Garment inseam length in centimetres.",
    )


# ============================================================
# Garment Response
# ============================================================

class GarmentResponse(BaseModel):
    """
    Schema returned when a garment is retrieved from the API.
    """

    garment_id: UUID
    user_id: UUID

    chest_width: float
    waist_width: float
    hip_width: float
    shoulder_width: float
    inseam: float

    created_at: datetime

    # Allows Pydantic to create the response directly from
    # a SQLAlchemy Garment model instance.
    model_config = ConfigDict(from_attributes=True)