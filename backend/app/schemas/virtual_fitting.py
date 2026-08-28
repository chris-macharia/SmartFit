"""
Pydantic schemas for the SmartFit Virtual Fitting API.

This module defines the data structures used when requesting
and returning virtual fitting results.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# Virtual Fitting Creation
# ============================================================

class VirtualFittingCreate(BaseModel):
    """
    Schema used when requesting a virtual fitting.

    The user_id is intentionally excluded because the
    authenticated user's ID is obtained from the JWT.
    """

    garment_id: UUID
    avatar_id: UUID


# ============================================================
# Virtual Fitting Response
# ============================================================

class VirtualFittingResponse(BaseModel):
    """
    Schema returned after a virtual fitting is completed.
    """

    fitting_id: UUID
    user_id: UUID
    garment_id: UUID
    avatar_id: UUID
    recommended_size: str
    fit_result: str
    created_at: datetime

    # Allow Pydantic to construct this schema directly
    # from the SQLAlchemy VirtualFitting model.
    model_config = ConfigDict(
        from_attributes=True
    )