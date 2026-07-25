"""
SmartFit database models.

This module imports the application's SQLAlchemy models so that
they are registered with the shared SQLAlchemy Base metadata.
"""

from app.models.avatar import Avatar
from app.models.body_measurements import BodyMeasurement
from app.models.garment import Garment
from app.models.user import User
from app.models.video import Video
from app.models.virtual_fitting import VirtualFitting


# Define the public models exposed by this package.
#
# Additional SmartFit models will be added here as they are
# implemented.
__all__ = [
    "User",
    "Garment",
    "Video",
    "BodyMeasurement",
    "Avatar",
    "VirtualFitting",
]