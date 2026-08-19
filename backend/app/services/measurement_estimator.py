"""
Body-measurement estimation helpers for SmartFit.

This module deliberately contains no OpenCV, MediaPipe, database, or
HTTP code. Keeping the mathematical estimation logic independent makes
it deterministic and straightforward to unit test.

The first SmartFit estimator is intentionally conservative. It returns
height, shoulder width, and inseam only. Chest, waist, and hip values
require silhouette analysis and controlled front/side views, so they
remain unavailable until that later refinement is implemented.
"""

from dataclasses import dataclass
from math import hypot
from statistics import median


# The landmark names used by the pose extraction service. Using readable
# names here avoids leaking MediaPipe implementation details into the
# estimation calculations.
LEFT_SHOULDER = "left_shoulder"
RIGHT_SHOULDER = "right_shoulder"
LEFT_HIP = "left_hip"
RIGHT_HIP = "right_hip"
LEFT_ANKLE = "left_ankle"
RIGHT_ANKLE = "right_ankle"
NOSE = "nose"


class MeasurementEstimationError(ValueError):
    """Raised when valid pose data is insufficient for an estimate."""


@dataclass(frozen=True)
class LandmarkPoint:
    """A normalized two-dimensional landmark from one video frame."""

    x: float
    y: float
    visibility: float


@dataclass(frozen=True)
class PoseFrame:
    """A validated collection of body landmarks at one video timestamp."""

    timestamp_ms: int
    landmarks: dict[str, LandmarkPoint]


@dataclass(frozen=True)
class MeasurementEstimate:
    """The safely supportable outputs of the first SmartFit estimator."""

    height_cm: float
    shoulder_width_cm: float
    inseam_cm: float
    confidence_score: float
    processing_version: str = "pose-v1"


def _distance(first: LandmarkPoint, second: LandmarkPoint) -> float:
    """Return the normalized two-dimensional distance between landmarks."""

    return hypot(first.x - second.x, first.y - second.y)


def _required_landmarks(frame: PoseFrame) -> tuple[LandmarkPoint, ...]:
    """Return the landmarks needed for the initial body estimates."""

    required_names = (
        NOSE,
        LEFT_SHOULDER,
        RIGHT_SHOULDER,
        LEFT_HIP,
        RIGHT_HIP,
        LEFT_ANKLE,
        RIGHT_ANKLE,
    )

    try:
        return tuple(frame.landmarks[name] for name in required_names)
    except KeyError as exc:
        raise MeasurementEstimationError(
            "A required body landmark was not detected."
        ) from exc


def estimate_measurements(
    pose_frames: list[PoseFrame],
    user_height_cm: float,
) -> MeasurementEstimate:
    """
    Estimate basic body measurements from stable pose landmark frames.

    The user's declared height calibrates normalized image proportions to
    centimetres. Median values are used so one unusual frame has limited
    influence on the final estimate.

    Args:
        pose_frames: Validated frames returned by the pose extractor.
        user_height_cm: User-declared height in centimetres.

    Returns:
        MeasurementEstimate: Height, shoulder width, inseam, and confidence.

    Raises:
        MeasurementEstimationError: If the input cannot produce an estimate.
    """

    if not 100 <= user_height_cm <= 250:
        raise MeasurementEstimationError(
            "The supplied height is outside SmartFit's supported range."
        )

    if len(pose_frames) < 3:
        raise MeasurementEstimationError(
            "At least three clear full-body frames are required."
        )

    shoulder_widths: list[float] = []
    inseams: list[float] = []
    frame_confidences: list[float] = []

    for frame in pose_frames:
        (
            nose,
            left_shoulder,
            right_shoulder,
            left_hip,
            right_hip,
            left_ankle,
            right_ankle,
        ) = _required_landmarks(frame)

        # The vertical distance from nose to ankles is the scale reference
        # for this frame. Frames with an implausibly small body height are
        # unusable because the person is likely cropped or badly detected.
        ankle_y = (left_ankle.y + right_ankle.y) / 2
        normalized_body_height = abs(ankle_y - nose.y)

        if normalized_body_height < 0.1:
            continue

        centimetres_per_normalized_unit = (
            user_height_cm / normalized_body_height
        )

        shoulder_widths.append(
            _distance(left_shoulder, right_shoulder)
            * centimetres_per_normalized_unit
        )

        # Estimate inseam from the median hip position to the median ankle
        # position. This is a body proportion estimate, not a tailor-grade
        # inside-leg measurement.
        hip_midpoint = LandmarkPoint(
            x=(left_hip.x + right_hip.x) / 2,
            y=(left_hip.y + right_hip.y) / 2,
            visibility=(left_hip.visibility + right_hip.visibility) / 2,
        )
        ankle_midpoint = LandmarkPoint(
            x=(left_ankle.x + right_ankle.x) / 2,
            y=(left_ankle.y + right_ankle.y) / 2,
            visibility=(left_ankle.visibility + right_ankle.visibility) / 2,
        )
        inseams.append(
            _distance(hip_midpoint, ankle_midpoint)
            * centimetres_per_normalized_unit
        )

        frame_confidences.append(
            sum(point.visibility for point in _required_landmarks(frame))
            / 7
        )

    if len(shoulder_widths) < 3 or len(inseams) < 3:
        raise MeasurementEstimationError(
            "SmartFit could not find enough clear full-body frames."
        )

    # Confidence combines landmark visibility and the number of usable
    # observations. More than ten good frames does not increase confidence
    # further in this initial version.
    visibility_confidence = median(frame_confidences)
    frame_count_confidence = min(len(shoulder_widths) / 10, 1.0)
    confidence_score = round(
        min(visibility_confidence * frame_count_confidence, 1.0),
        2,
    )

    return MeasurementEstimate(
        height_cm=round(user_height_cm, 2),
        shoulder_width_cm=round(median(shoulder_widths), 2),
        inseam_cm=round(median(inseams), 2),
        confidence_score=confidence_score,
    )
