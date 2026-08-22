"""
3D avatar generation helpers for SmartFit.

This module converts SmartFit body measurements into a simple
parameterized 3D avatar and exports the result as a binary GLB file.

The v1 avatar is intentionally simple. Its proportions are based on
the measurements currently produced by the SmartFit measurement
estimation pipeline.

This module contains no FastAPI, authentication, or database-session
logic.
"""

import trimesh

from app.models.body_measurements import BodyMeasurement


class AvatarGenerationError(ValueError):
    """Raised when a body measurement cannot produce an avatar."""


def _validate_measurements(
    measurement: BodyMeasurement,
) -> None:
    """
    Validate the measurements required for v1 avatar generation.
    """

    if measurement.height is None or float(measurement.height) <= 0:
        raise AvatarGenerationError(
            "A valid body height is required to generate an avatar."
        )

    if (
        measurement.shoulder_width is None
        or float(measurement.shoulder_width) <= 0
    ):
        raise AvatarGenerationError(
            "A valid shoulder width is required to generate an avatar."
        )

    if measurement.inseam is None or float(measurement.inseam) <= 0:
        raise AvatarGenerationError(
            "A valid inseam is required to generate an avatar."
        )


def _create_box(
    width: float,
    depth: float,
    height: float,
    x: float,
    y: float,
    z: float,
) -> trimesh.Trimesh:
    """
    Create a rectangular body component at the supplied position.
    """

    mesh = trimesh.creation.box(
        extents=[
            width,
            depth,
            height,
        ]
    )

    mesh.apply_translation(
        [
            x,
            y,
            z,
        ]
    )

    return mesh


def generate_avatar_glb(
    measurement: BodyMeasurement,
) -> bytes:
    """
    Generate a simple proportional GLB avatar.

    The avatar is constructed from basic 3D primitives using the
    measurements currently available from SmartFit.

    Args:
        measurement:
            Persisted BodyMeasurement used as the avatar source.

    Returns:
        Binary GLB data.

    Raises:
        AvatarGenerationError:
            If the required measurements are invalid.
    """

    _validate_measurements(measurement)

    # --------------------------------------------------------
    # Convert measurements from centimetres to metres.
    # --------------------------------------------------------

    height = float(measurement.height) / 100.0
    shoulder_width = (
        float(measurement.shoulder_width) / 100.0
    )
    inseam = float(measurement.inseam) / 100.0

    # --------------------------------------------------------
    # Derive v1 body proportions.
    # --------------------------------------------------------

    # The current estimator gives us total height and inseam.
    # The remaining body height is therefore used as a simple
    # torso/head region.
    upper_body_height = max(
        height - inseam,
        height * 0.40,
    )

    head_height = height * 0.12

    torso_height = max(
        upper_body_height - head_height,
        height * 0.25,
    )

    torso_width = max(
        shoulder_width * 0.75,
        height * 0.18,
    )

    torso_depth = torso_width * 0.55

    leg_width = max(
        shoulder_width * 0.20,
        height * 0.055,
    )

    leg_depth = leg_width

    arm_width = max(
        shoulder_width * 0.12,
        height * 0.035,
    )

    arm_length = max(
        height * 0.28,
        shoulder_width * 1.20,
    )

    # --------------------------------------------------------
    # Head.
    # --------------------------------------------------------

    head = trimesh.creation.icosphere(
        radius=head_height / 2.0,
        subdivisions=2,
    )

    head.apply_translation(
        [
            0.0,
            0.0,
            height - (head_height / 2.0),
        ]
    )

    # --------------------------------------------------------
    # Torso.
    # --------------------------------------------------------

    torso = _create_box(
        width=torso_width,
        depth=torso_depth,
        height=torso_height,
        x=0.0,
        y=0.0,
        z=inseam + (torso_height / 2.0),
    )

    # --------------------------------------------------------
    # Legs.
    # --------------------------------------------------------

    leg_offset = max(
        shoulder_width * 0.18,
        leg_width * 0.75,
    )

    left_leg = _create_box(
        width=leg_width,
        depth=leg_depth,
        height=inseam,
        x=-leg_offset,
        y=0.0,
        z=inseam / 2.0,
    )

    right_leg = _create_box(
        width=leg_width,
        depth=leg_depth,
        height=inseam,
        x=leg_offset,
        y=0.0,
        z=inseam / 2.0,
    )

    # --------------------------------------------------------
    # Arms.
    # --------------------------------------------------------

    arm_z = inseam + torso_height * 0.72

    arm_center_x = (
        shoulder_width / 2.0
        + arm_width / 2.0
    )

    left_arm = _create_box(
        width=arm_width,
        depth=arm_width,
        height=arm_length,
        x=-arm_center_x,
        y=0.0,
        z=arm_z - (arm_length / 2.0),
    )

    right_arm = _create_box(
        width=arm_width,
        depth=arm_width,
        height=arm_length,
        x=arm_center_x,
        y=0.0,
        z=arm_z - (arm_length / 2.0),
    )

    # --------------------------------------------------------
    # Build the scene.
    # --------------------------------------------------------

    scene = trimesh.Scene(
        geometry={
            "head": head,
            "torso": torso,
            "left_leg": left_leg,
            "right_leg": right_leg,
            "left_arm": left_arm,
            "right_arm": right_arm,
        }
    )

    # --------------------------------------------------------
    # Export binary GLB.
    # --------------------------------------------------------

    glb_data = scene.export(
        file_type="glb",
    )

    if not isinstance(glb_data, bytes) or not glb_data:
        raise AvatarGenerationError(
            "SmartFit failed to generate a valid GLB avatar."
        )

    return glb_data