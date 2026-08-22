"""
Tests for the SmartFit avatar service.

This module verifies avatar generation, persistence, ownership
validation, duplicate prevention, and GLB file creation.
"""

import uuid
from pathlib import Path

import trimesh

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.avatar import Avatar
from app.models.body_measurements import BodyMeasurement
from app.models.user import User
from app.models.video import Video
from app.services.avatar_service import (
    create_avatar,
)


# ============================================================
# Test Helpers
# ============================================================


def create_test_user(
    email: str,
    password: str,
):
    """Create a test user."""

    db = SessionLocal()

    try:
        user = User(
            full_name="Avatar Test User",
            email=email,
            hashed_password=hash_password(password),
            role="customer",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def delete_test_user(email: str):
    """
    Delete a test user and associated avatar/measurement/video
    records and physical files.
    """

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user is None:
            return

        videos = list(user.videos)

        for video in videos:

            measurements = (
                db.query(BodyMeasurement)
                .filter(
                    BodyMeasurement.video_id
                    == video.video_id
                )
                .all()
            )

            for measurement in measurements:

                avatars = (
                    db.query(Avatar)
                    .filter(
                        Avatar.measurement_id
                        == measurement.measurement_id
                    )
                    .all()
                )

                for avatar in avatars:
                    avatar_path = Path(
                        avatar.avatar_path
                    )

                    if avatar_path.exists():
                        avatar_path.unlink()

                    db.delete(avatar)

                db.delete(measurement)

        db.flush()

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def create_test_measurement(
    user: User,
):
    """
    Create a completed video and body measurement for a test user.
    """

    db = SessionLocal()

    try:
        video = Video(
            user_id=user.user_id,
            video_path="uploads/videos/avatar-test.mp4",
            processing_status="completed",
            user_height_cm=175.0,
            processing_error=None,
        )

        db.add(video)
        db.flush()

        measurement = BodyMeasurement(
            video_id=video.video_id,
            height=175.0,
            shoulder_width=64.89,
            inseam=90.23,
            chest=None,
            waist=None,
            hips=None,
            confidence_score=0.96,
            processing_version="pose-v1",
        )

        db.add(measurement)
        db.commit()
        db.refresh(measurement)

        return measurement

    finally:
        db.close()


# ============================================================
# Avatar Creation Tests
# ============================================================


def test_create_avatar_generates_glb_and_database_record():
    """
    Verify that a valid body measurement produces both a physical
    GLB file and an Avatar database record.
    """

    email = "avatar.service.create@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        measurement = create_test_measurement(
            user
        )

        db = SessionLocal()

        try:
            avatar = create_avatar(
                db=db,
                measurement_id=measurement.measurement_id,
                user_id=user.user_id,
            )

            # ------------------------------------------------
            # Verify database record.
            # ------------------------------------------------

            assert avatar is not None
            assert avatar.avatar_id is not None
            assert (
                avatar.measurement_id
                == measurement.measurement_id
            )
            assert avatar.avatar_path.endswith(".glb")

            # ------------------------------------------------
            # Verify physical file.
            # ------------------------------------------------

            avatar_path = Path(
                avatar.avatar_path
            )

            assert avatar_path.exists()
            assert avatar_path.is_file()
            assert avatar_path.stat().st_size > 0

            # ------------------------------------------------
            # Verify the GLB can actually be loaded.
            # ------------------------------------------------

            scene = trimesh.load(
                avatar_path,
                file_type="glb",
            )

            assert scene is not None

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_create_avatar_rejects_duplicate_measurement():
    """
    Verify that a body measurement cannot generate two avatars.
    """

    email = "avatar.service.duplicate@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        measurement = create_test_measurement(
            user
        )

        db = SessionLocal()

        try:
            first_avatar = create_avatar(
                db=db,
                measurement_id=measurement.measurement_id,
                user_id=user.user_id,
            )

            assert first_avatar is not None

            try:
                create_avatar(
                    db=db,
                    measurement_id=measurement.measurement_id,
                    user_id=user.user_id,
                )

                assert False, (
                    "Expected duplicate avatar creation "
                    "to raise ValueError."
                )

            except ValueError as exc:
                assert str(exc) == (
                    "An avatar already exists for "
                    "this body measurement."
                )

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_user_cannot_generate_avatar_from_another_users_measurement():
    """
    Verify that avatar generation enforces measurement ownership.
    """

    owner_email = "avatar.service.owner@example.com"
    other_email = "avatar.service.other@example.com"
    password = "SecurePassword123"

    delete_test_user(owner_email)
    delete_test_user(other_email)

    try:
        owner = create_test_user(
            email=owner_email,
            password=password,
        )

        other_user = create_test_user(
            email=other_email,
            password=password,
        )

        measurement = create_test_measurement(
            owner
        )

        db = SessionLocal()

        try:
            try:
                create_avatar(
                    db=db,
                    measurement_id=measurement.measurement_id,
                    user_id=other_user.user_id,
                )

                assert False, (
                    "Expected unauthorized measurement "
                    "access to raise ValueError."
                )

            except ValueError as exc:
                assert str(exc) == (
                    "Body measurement not found."
                )

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)