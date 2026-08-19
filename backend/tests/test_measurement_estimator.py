"""Unit tests for the deterministic Milestone 5 measurement estimator."""

import pytest

from app.services.measurement_estimator import (
    LandmarkPoint,
    MeasurementEstimationError,
    PoseFrame,
    estimate_measurements,
)


def _pose_frame(timestamp_ms: int) -> PoseFrame:
    """Create a stable, complete synthetic pose frame for calculation tests."""

    return PoseFrame(
        timestamp_ms=timestamp_ms,
        landmarks={
            "nose": LandmarkPoint(0.5, 0.1, 0.95),
            "left_shoulder": LandmarkPoint(0.4, 0.3, 0.95),
            "right_shoulder": LandmarkPoint(0.6, 0.3, 0.95),
            "left_hip": LandmarkPoint(0.43, 0.6, 0.95),
            "right_hip": LandmarkPoint(0.57, 0.6, 0.95),
            "left_ankle": LandmarkPoint(0.43, 0.9, 0.95),
            "right_ankle": LandmarkPoint(0.57, 0.9, 0.95),
        },
    )


def test_estimate_measurements_uses_declared_height_as_scale():
    """Verify normalized landmark distances are converted to centimetres."""

    estimate = estimate_measurements(
        pose_frames=[_pose_frame(0), _pose_frame(500), _pose_frame(1000)],
        user_height_cm=180.0,
    )

    assert estimate.height_cm == 180.0
    assert estimate.shoulder_width_cm == pytest.approx(45.0)
    assert estimate.inseam_cm == pytest.approx(67.5)
    assert 0 < estimate.confidence_score <= 1
    assert estimate.processing_version == "pose-v1"


def test_estimate_measurements_requires_three_clear_frames():
    """Verify the estimator rejects unreliable single-frame measurements."""

    with pytest.raises(MeasurementEstimationError):
        estimate_measurements(
            pose_frames=[_pose_frame(0), _pose_frame(500)],
            user_height_cm=180.0,
        )
