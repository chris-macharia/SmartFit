"""
Pydantic schemas for the SmartFit Virtual Fitting API.

This module defines the data structures used when receiving
virtual fitting requests and returning fitting results.

The schemas are separate from the SQLAlchemy VirtualFitting model:

- SQLAlchemy defines how fitting results are stored in PostgreSQL.
- Pydantic defines how fitting data enters and leaves the API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Virtual Fitting Creation
# ============================================================

class VirtualFittingCreate(BaseModel):
    """
    Schema used when creating a new virtual fitting.

    The authenticated user's ID is intentionally excluded.

    The backend obtains the user ID from the authenticated JWT.
    """

    garment_id: UUID = Field(
        ...,
        description="UUID of the garment to evaluate.",
    )

    avatar_id: UUID = Field(
        ...,
        description="UUID of the user's digital avatar.",
    )


# ============================================================
# Virtual Fitting Response
# ============================================================

class VirtualFittingResponse(BaseModel):
    """
    Schema returned after a virtual fitting is created
    or retrieved.
    """

    fitting_id: UUID

    user_id: UUID

    garment_id: UUID

    avatar_id: UUID

    recommended_size: str

    fit_result: str

    created_at: datetime

    # Allow Pydantic to construct the response directly
    # from a SQLAlchemy VirtualFitting model instance.
    model_config = ConfigDict(
        from_attributes=True,
    )