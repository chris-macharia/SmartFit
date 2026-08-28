"""
Virtual fitting service for SmartFit.

This module contains the application logic used to perform a
virtual clothing fitting.

The initial Milestone 8 implementation intentionally uses a
simple measurement-comparison algorithm.

Body measurements are interpreted as follows:

    BodyMeasurement.chest
        -> garment chest_width

    BodyMeasurement.waist
        -> garment waist_width

    BodyMeasurement.hips
        -> garment hip_width

    BodyMeasurement.shoulder_width
        -> garment shoulder_width

    BodyMeasurement.inseam
        -> garment inseam

The algorithm compares each garment measurement with the
corresponding body measurement.

The overall fitting result is determined from the measurement
differences:

    Tight
        One or more important garment measurements are
        significantly smaller than the corresponding body
        measurement.

    Loose
        The garment is substantially larger than the body
        measurements.

    Good Fit
        The garment measurements fall within the acceptable
        fitting range.

The implementation is deliberately simple so that the fitting
workflow can be established before introducing more advanced
computer-vision or cloth-simulation techniques.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.avatar import Avatar
from app.models.body_measurements import BodyMeasurement
from app.models.garment import Garment
from app.models.virtual_fitting import VirtualFitting


# ============================================================
# Fitting Thresholds
# ============================================================

# A garment measurement below the body measurement by more
# than this percentage is considered too small.
#
# Example:
#
# Body chest = 50 cm
# Garment chest = 44 cm
#
# Difference = -12%
#
# Therefore the garment is considered tight.
TIGHT_THRESHOLD = -0.10


# A garment measurement above the body measurement by more
# than this percentage is considered substantially loose.
#
# Example:
#
# Body chest = 50 cm
# Garment chest = 60 cm
#
# Difference = +20%
#
# Therefore the garment is considered loose.
LOOSE_THRESHOLD = 0.15


# Measurements such as shoulder width and inseam are important
# to the overall fit. A garment being significantly smaller in
# these areas should therefore contribute to a Tight result.
IMPORTANT_MEASUREMENTS = (
    "shoulder_width",
    "inseam",
)


# ============================================================
# Measurement Comparison
# ============================================================


def _calculate_difference(
    body_measurement: float,
    garment_measurement: float,
) -> float:
    """
    Calculate the relative difference between a garment
    measurement and the corresponding body measurement.

    The result is expressed as a decimal ratio.

    Examples:

        body = 50
        garment = 55

        result = 0.10

        This represents a garment that is 10% larger.

    Args:
        body_measurement:
            Customer's corresponding body measurement.

        garment_measurement:
            Corresponding garment measurement.

    Returns:
        float:
            Relative measurement difference.
    """

    if body_measurement <= 0:
        raise ValueError(
            "Body measurement must be greater than zero."
        )

    return (
        garment_measurement - body_measurement
    ) / body_measurement


# ============================================================
# Recommended Size
# ============================================================


def _determine_recommended_size(
    chest: float,
) -> str:
    """
    Determine a simple recommended clothing size from the
    customer's chest width.

    This is intentionally a basic first-version size mapping.

    The size thresholds can be replaced later with retailer-
    specific sizing charts.

    Args:
        chest:
            Customer's chest width in centimetres.

    Returns:
        str:
            Recommended clothing size.
    """

    if chest < 44:
        return "XS"

    if chest < 48:
        return "S"

    if chest < 52:
        return "M"

    if chest < 56:
        return "L"

    if chest < 60:
        return "XL"

    return "XXL"


# ============================================================
# Fit Result
# ============================================================


def _determine_fit_result(
    body_measurements: BodyMeasurement,
    garment: Garment,
) -> str:
    """
    Determine the overall fit between a customer's body and
    a garment.

    The current algorithm compares:

        chest
        waist
        hips
        shoulder width
        inseam

    A measurement difference is calculated as:

        (garment - body) / body

    Therefore:

        Negative value
            Garment is smaller than the body.

        Positive value
            Garment is larger than the body.

    The fitting rules are:

        Tight
            At least one measurement is 10% or more smaller.

        Loose
            No tight measurement exists and at least two
            measurements are 15% or more larger.

        Good Fit
            Everything else.

    Args:
        body_measurements:
            Customer's body measurements.

        garment:
            Selected garment.

    Returns:
        str:
            One of:

                "Good Fit"
                "Tight"
                "Loose"
    """

    comparisons = {
        "chest": _calculate_difference(
            float(body_measurements.chest),
            float(garment.chest_width),
        ),
        "waist": _calculate_difference(
            float(body_measurements.waist),
            float(garment.waist_width),
        ),
        "hips": _calculate_difference(
            float(body_measurements.hips),
            float(garment.hip_width),
        ),
        "shoulder_width": _calculate_difference(
            float(body_measurements.shoulder_width),
            float(garment.shoulder_width),
        ),
        "inseam": _calculate_difference(
            float(body_measurements.inseam),
            float(garment.inseam),
        ),
    }

    # --------------------------------------------------------
    # Check for missing body measurements.
    # --------------------------------------------------------

    # Chest, waist and hips may currently be nullable in the
    # database because the computer-vision pipeline may not
    # always estimate them.
    #
    # The initial fitting algorithm requires all five values.
    if (
        body_measurements.chest is None
        or body_measurements.waist is None
        or body_measurements.hips is None
    ):
        raise ValueError(
            "Complete body measurements are required "
            "for virtual fitting."
        )

    # --------------------------------------------------------
    # Check for Tight Fit.
    # --------------------------------------------------------

    # A significant shortage in any measurement means the
    # garment is too small in that area.
    for difference in comparisons.values():

        if difference <= TIGHT_THRESHOLD:
            return "Tight"

    # --------------------------------------------------------
    # Check for Loose Fit.
    # --------------------------------------------------------

    # Count substantially oversized measurements.
    loose_measurements = sum(
        difference >= LOOSE_THRESHOLD
        for difference in comparisons.values()
    )

    # Require at least two measurements to be substantially
    # larger before classifying the entire garment as loose.
    if loose_measurements >= 2:
        return "Loose"

    # --------------------------------------------------------
    # Otherwise the garment is considered a good fit.
    # --------------------------------------------------------

    return "Good Fit"


# ============================================================
# Create Virtual Fitting
# ============================================================


def create_virtual_fitting(
    db: Session,
    user_id: uuid.UUID,
    garment_id: uuid.UUID,
    avatar_id: uuid.UUID,
) -> VirtualFitting:
    """
    Perform and persist a virtual fitting.

    The authenticated user's ID is used to ensure that the
    selected avatar belongs to the requesting user.

    The garment may belong to a different user because garments
    are registered by retailers and selected by customers.

    Args:
        db:
            Active SQLAlchemy database session.

        user_id:
            UUID of the authenticated customer.

        garment_id:
            UUID of the selected garment.

        avatar_id:
            UUID of the customer's generated avatar.

    Returns:
        VirtualFitting:
            Newly created virtual fitting record.

    Raises:
        ValueError:
            If the avatar, garment, or associated measurement
            cannot be found.

            If the avatar does not belong to the authenticated
            user.

            If required body measurements are unavailable.

            If the same fitting already exists.
    """

    # --------------------------------------------------------
    # Find Avatar.
    # --------------------------------------------------------

    avatar = (
        db.query(Avatar)
        .filter(
            Avatar.avatar_id == avatar_id,
        )
        .first()
    )

    if avatar is None:
        raise ValueError(
            "Avatar not found."
        )

    # --------------------------------------------------------
    # Retrieve Body Measurement.
    # --------------------------------------------------------

    measurement = (
        db.query(BodyMeasurement)
        .filter(
            BodyMeasurement.measurement_id
            == avatar.measurement_id,
        )
        .first()
    )

    if measurement is None:
        raise ValueError(
            "Body measurement not found."
        )

    # --------------------------------------------------------
    # Verify Avatar Ownership.
    # --------------------------------------------------------

    # The measurement belongs to a Video.
    #
    # The Video contains the user_id of the customer who
    # uploaded the body video.
    video = measurement.video

    if video is None:
        raise ValueError(
            "Body measurement video not found."
        )

    if video.user_id != user_id:
        raise ValueError(
            "Avatar not found."
        )

    # --------------------------------------------------------
    # Find Garment.
    # --------------------------------------------------------

    garment = (
        db.query(Garment)
        .filter(
            Garment.garment_id == garment_id,
        )
        .first()
    )

    if garment is None:
        raise ValueError(
            "Garment not found."
        )

# --------------------------------------------------------
# Prevent Duplicate Fitting.
# --------------------------------------------------------

    existing_fitting = (
        db.query(VirtualFitting)
        .filter(
            VirtualFitting.user_id == user_id,
            VirtualFitting.garment_id == garment_id,
            VirtualFitting.avatar_id == avatar_id,
        )
        .first()
    )

    if existing_fitting is not None:
        raise ValueError(
            "A virtual fitting already exists "
            "for this avatar and garment."
        )


    # --------------------------------------------------------
    # Determine Fit.
    # --------------------------------------------------------

    fit_result = _determine_fit_result(
        body_measurements=measurement,
        garment=garment,
    )

    # --------------------------------------------------------
    # Determine Recommended Size.
    # --------------------------------------------------------

    if measurement.chest is None:
        raise ValueError(
            "Complete body measurements are required "
            "for virtual fitting."
        )

    recommended_size = _determine_recommended_size(
        chest=float(measurement.chest),
    )

    # --------------------------------------------------------
    # Create VirtualFitting Record.
    # --------------------------------------------------------

    fitting = VirtualFitting(
        fitting_id=uuid.uuid4(),
        user_id=user_id,
        garment_id=garment_id,
        avatar_id=avatar_id,
        recommended_size=recommended_size,
        fit_result=fit_result,
    )

    # --------------------------------------------------------
    # Persist Result.
    # --------------------------------------------------------

    try:
        db.add(fitting)
        db.commit()
        db.refresh(fitting)

    except Exception as exc:
        db.rollback()

        raise RuntimeError(
            "Unable to create the virtual fitting record."
        ) from exc

    return fitting


# ============================================================
# Retrieve Virtual Fitting
# ============================================================


def get_virtual_fitting_by_id(
    db: Session,
    fitting_id: uuid.UUID,
    user_id: uuid.UUID,
) -> VirtualFitting | None:
    """
    Retrieve a virtual fitting belonging to the authenticated
    user.

    Ownership is enforced by including user_id in the database
    query.

    Args:
        db:
            Active SQLAlchemy database session.

        fitting_id:
            UUID of the virtual fitting.

        user_id:
            UUID of the authenticated customer.

    Returns:
        VirtualFitting | None:
            The fitting if it exists and belongs to the user.
            Otherwise None.
    """

    return (
        db.query(VirtualFitting)
        .filter(
            VirtualFitting.fitting_id == fitting_id,
            VirtualFitting.user_id == user_id,
        )
        .first()
    )
