"""
Background processing orchestration for SmartFit uploaded videos.

This module owns video state transitions and database persistence. It
creates its own database session because FastAPI request sessions are
closed before background tasks finish.
"""

import logging
from pathlib import Path
from uuid import UUID

from app.db.database import SessionLocal
from app.models.body_measurements import BodyMeasurement
from app.models.video import Video
from app.services.measurement_estimator import (
    MeasurementEstimationError,
    estimate_measurements,
)
from app.services.pose_estimator import PoseExtractionError, extract_pose_landmarks


logger = logging.getLogger(__name__)


def _mark_failed(video: Video, error_message: str) -> None:
    """Store a safe processing failure message on an existing video record."""

    video.processing_status = "failed"
    video.processing_error = error_message


def process_video(video_id: UUID) -> None:
    """
    Process one uploaded video in the background.

    The function never exposes low-level server exceptions through the
    database. Technical details are logged while customers receive an
    actionable, safe message through the video status API.
    """

    db = SessionLocal()

    try:
        video = db.query(Video).filter(Video.video_id == video_id).first()

        # A user might delete their upload before the background task starts.
        if video is None:
            return

        if video.user_height_cm is None:
            _mark_failed(video, "A valid height is required for processing.")
            db.commit()
            return

        video.processing_status = "processing"
        video.processing_error = None
        db.commit()

        pose_frames = extract_pose_landmarks(Path(video.video_path))
        estimate = estimate_measurements(
            pose_frames=pose_frames,
            user_height_cm=float(video.user_height_cm),
        )

        # Video-to-measurement is one-to-one. If a later retry is introduced,
        # replace the existing record rather than creating a duplicate.
        measurement = (
            db.query(BodyMeasurement)
            .filter(BodyMeasurement.video_id == video.video_id)
            .first()
        )

        if measurement is None:
            measurement = BodyMeasurement(video_id=video.video_id)
            db.add(measurement)

        measurement.height = estimate.height_cm
        measurement.shoulder_width = estimate.shoulder_width_cm
        measurement.inseam = estimate.inseam_cm
        measurement.chest = None
        measurement.waist = None
        measurement.hips = None
        measurement.confidence_score = estimate.confidence_score
        measurement.processing_version = estimate.processing_version

        video.processing_status = "completed"
        video.processing_error = None
        db.commit()

    except (PoseExtractionError, MeasurementEstimationError) as exc:
        db.rollback()
        video = db.query(Video).filter(Video.video_id == video_id).first()

        if video is not None:
            _mark_failed(video, str(exc))
            db.commit()

    except Exception:
        db.rollback()
        logger.exception("Unexpected error while processing SmartFit video %s", video_id)
        video = db.query(Video).filter(Video.video_id == video_id).first()

        if video is not None:
            _mark_failed(video, "SmartFit could not process this video.")
            db.commit()

    finally:
        db.close()
