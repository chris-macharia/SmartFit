"""
MediaPipe pose extraction for SmartFit body videos.

Only this module knows about OpenCV and MediaPipe. It converts sampled
video frames into the small, testable PoseFrame format used by the
measurement estimator.
"""

from pathlib import Path

from app.core.config import settings
from app.services.measurement_estimator import LandmarkPoint, PoseFrame


class PoseExtractionError(RuntimeError):
    """Raised when SmartFit cannot extract usable body poses from a video."""


# MediaPipe landmark indices for the points required by pose-v1.
LANDMARK_INDICES = {
    "nose": 0,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
    "left_ankle": 27,
    "right_ankle": 28,
}

MINIMUM_VISIBILITY = 0.60
SAMPLE_RATE_FPS = 2.0


def _model_path() -> Path:
    """Resolve the configured MediaPipe model path from the backend folder."""

    configured_path = Path(settings.POSE_LANDMARKER_MODEL_PATH)

    if configured_path.is_absolute():
        return configured_path

    # Resolve relative paths from the backend directory rather than from the
    # process working directory. This keeps Uvicorn and test invocations
    # consistent whether they start in backend/ or the repository root.
    backend_directory = Path(__file__).resolve().parents[2]

    return backend_directory / configured_path


def _to_pose_frame(result, timestamp_ms: int) -> PoseFrame | None:
    """Convert one MediaPipe result into a validated SmartFit pose frame."""

    # SmartFit supports one customer per uploaded body video. Empty results
    # and multiple detected poses are rejected rather than guessed about.
    if len(result.pose_landmarks) != 1:
        return None

    landmarks = result.pose_landmarks[0]
    selected_landmarks: dict[str, LandmarkPoint] = {}

    for name, index in LANDMARK_INDICES.items():
        landmark = landmarks[index]
        visibility = float(landmark.visibility or 0.0)

        if visibility < MINIMUM_VISIBILITY:
            return None

        selected_landmarks[name] = LandmarkPoint(
            x=float(landmark.x),
            y=float(landmark.y),
            visibility=visibility,
        )

    return PoseFrame(
        timestamp_ms=timestamp_ms,
        landmarks=selected_landmarks,
    )


def extract_pose_landmarks(video_path: Path) -> list[PoseFrame]:
    """
    Sample a video and return high-quality, full-body pose landmark frames.

    Args:
        video_path: Local path of the uploaded video file.

    Raises:
        PoseExtractionError: If dependencies, model, video, or poses fail.
    """

    try:
        import cv2
        import mediapipe as mp
    except ImportError as exc:
        raise PoseExtractionError(
            "Video-processing dependencies are not installed."
        ) from exc

    if not video_path.is_file():
        raise PoseExtractionError("The uploaded video file could not be found.")

    model_path = _model_path()

    if not model_path.is_file():
        raise PoseExtractionError(
            "The pose detection model is not configured on the server."
        )

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise PoseExtractionError("SmartFit could not open the uploaded video.")

    source_fps = capture.get(cv2.CAP_PROP_FPS) or 0
    sample_every = max(int(round(source_fps / SAMPLE_RATE_FPS)), 1)
    valid_frames: list[PoseFrame] = []
    frame_index = 0
    previous_timestamp_ms = -1

    try:
        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=MINIMUM_VISIBILITY,
            min_pose_presence_confidence=MINIMUM_VISIBILITY,
            min_tracking_confidence=MINIMUM_VISIBILITY,
        )

        with mp.tasks.vision.PoseLandmarker.create_from_options(
            options
        ) as landmarker:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                if frame_index % sample_every != 0:
                    frame_index += 1
                    continue

                # MediaPipe video mode requires strictly increasing timestamps.
                # CAP_PROP_POS_MSEC is preferred, with a frame-index fallback
                # for videos whose decoder does not expose reliable timestamps.
                timestamp_ms = int(capture.get(cv2.CAP_PROP_POS_MSEC))

                if timestamp_ms <= previous_timestamp_ms:
                    if source_fps > 0:
                        timestamp_ms = int((frame_index / source_fps) * 1000)
                    else:
                        timestamp_ms = previous_timestamp_ms + 1

                timestamp_ms = max(timestamp_ms, previous_timestamp_ms + 1)
                previous_timestamp_ms = timestamp_ms
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame,
                )
                result = landmarker.detect_for_video(image, timestamp_ms)
                pose_frame = _to_pose_frame(result, timestamp_ms)

                if pose_frame is not None:
                    valid_frames.append(pose_frame)

                frame_index += 1

    except PoseExtractionError:
        raise
    except Exception as exc:
        raise PoseExtractionError(
            "SmartFit could not analyse the uploaded video."
        ) from exc
    finally:
        capture.release()

    if len(valid_frames) < 3:
        raise PoseExtractionError(
            "Please upload a clearer video with your full body visible."
        )

    return valid_frames
