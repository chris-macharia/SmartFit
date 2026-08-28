"""
Tests for the SmartFit virtual fitting service.

This module verifies virtual fitting creation, fit assessment,
ownership validation, duplicate prevention, and retrieval.

The current fitting algorithm intentionally uses simple
measurement comparisons:

- Garment measurements are compared with body measurements.
- A fitting is classified as Good Fit, Tight, or Loose.
- The algorithm currently treats chest, waist, hips, and
  shoulder values as width measurements.
"""

import uuid
from pathlib import Path

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models import (
    Avatar,
    BodyMeasurement,
    Garment,
    User,
    Video,
    VirtualFitting,
)
from app.services.virtual_fitting_service import (
    create_virtual_fitting,
    get_virtual_fitting_by_id,
)


# ============================================================
# Test Helpers
# ============================================================


def create_test_user(
    email: str,
    password: str,
    role: str = "customer",
):
    """
    Create a temporary test user.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Virtual Fitting Test User",
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def create_test_avatar(
    user: User,
):
    """
    Create the complete dependency chain required for a test avatar.

    The chain is:

        User
          ↓
        Video
          ↓
        BodyMeasurement
          ↓
        Avatar
    """

    db = SessionLocal()

    try:
        video = Video(
            user_id=user.user_id,
            video_path="uploads/videos/virtual-fitting-test.mp4",
            processing_status="completed",
            user_height_cm=175.0,
            processing_error=None,
        )

        db.add(video)
        db.flush()

        measurement = BodyMeasurement(
            video_id=video.video_id,
            height=175.0,
            chest=95.0,
            waist=80.0,
            hips=95.0,
            shoulder_width=45.0,
            inseam=80.0,
            confidence_score=0.96,
            processing_version="pose-v1",
        )

        db.add(measurement)
        db.flush()

        avatar = Avatar(
            measurement_id=measurement.measurement_id,
            avatar_path=(
                "uploads/avatars/"
                "virtual-fitting-test-avatar.glb"
            ),
        )

        db.add(avatar)
        db.commit()
        db.refresh(avatar)

        return avatar

    finally:
        db.close()


def create_test_garment(
    user: User,
    chest_width: float = 95.0,
    waist_width: float = 80.0,
    hip_width: float = 95.0,
    shoulder_width: float = 45.0,
    inseam: float = 80.0,
):
    """
    Create a temporary garment for testing.
    """

    db = SessionLocal()

    try:
        garment = Garment(
            user_id=user.user_id,
            chest_width=chest_width,
            waist_width=waist_width,
            hip_width=hip_width,
            shoulder_width=shoulder_width,
            inseam=inseam,
        )

        db.add(garment)
        db.commit()
        db.refresh(garment)

        return garment

    finally:
        db.close()


def delete_test_user(email: str):
    """
    Delete all test data belonging to a user.

    VirtualFitting records are explicitly removed first because
    VirtualFitting currently does not define SQLAlchemy ORM
    relationships with cascade behavior.

    Video -> BodyMeasurement -> Avatar records are then removed
    automatically through the configured SQLAlchemy cascades when
    the User is deleted.

    Generated avatar files are removed from disk before the
    database records are deleted.
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

        # --------------------------------------------------------
        # Remove physical avatar files.
        # --------------------------------------------------------
        #
        # Database cascading does not remove physical files.

        for video in list(user.videos):
            measurement = video.measurement

            if measurement is None:
                continue

            avatar = measurement.avatar

            if avatar is None:
                continue

            avatar_path = Path(avatar.avatar_path)

            if avatar_path.exists():
                avatar_path.unlink()

        # --------------------------------------------------------
        # Delete VirtualFitting records.
        # --------------------------------------------------------
        #
        # VirtualFitting has foreign keys but no ORM cascade
        # relationship to the User.

        db.query(VirtualFitting).filter(
            VirtualFitting.user_id == user.user_id
        ).delete(
            synchronize_session=False
        )

        # --------------------------------------------------------
        # Delete the User.
        # --------------------------------------------------------
        #
        # SQLAlchemy handles:
        #
        # User
        #   ├── Videos
        #   │     └── BodyMeasurements
        #   │           └── Avatars
        #   │
        #   └── Garments
        #
        # through the configured cascade relationships.

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# Virtual Fitting Creation Tests
# ============================================================


def test_create_virtual_fitting():
    """
    Verify that a valid avatar and garment can produce a
    VirtualFitting database record.
    """

    email = "virtual.fitting.service.create@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            assert fitting is not None
            assert fitting.fitting_id is not None
            assert isinstance(
                fitting.fitting_id,
                uuid.UUID,
            )

            assert (
                fitting.user_id
                == user.user_id
            )

            assert (
                fitting.avatar_id
                == avatar.avatar_id
            )

            assert (
                fitting.garment_id
                == garment.garment_id
            )

            assert fitting.recommended_size is not None
            assert fitting.fit_result is not None
            assert fitting.created_at is not None

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_virtual_fitting_returns_good_fit():
    """
    Verify that matching body and garment measurements produce
    a Good Fit result.
    """

    email = "virtual.fitting.service.good@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
            chest_width=95.0,
            waist_width=80.0,
            hip_width=95.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            assert fitting.fit_result == "Good Fit"

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_virtual_fitting_detects_tight_fit():
    """
    Verify that a garment smaller than the body measurements
    is classified as Tight.
    """

    email = "virtual.fitting.service.tight@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
            chest_width=85.0,
            waist_width=70.0,
            hip_width=85.0,
            shoulder_width=40.0,
            inseam=75.0,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            assert fitting.fit_result == "Tight"

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_virtual_fitting_detects_loose_fit():
    """
    Verify that a garment larger than the body measurements
    is classified as Loose.
    """

    email = "virtual.fitting.service.loose@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
            chest_width=110.0,
            waist_width=95.0,
            hip_width=110.0,
            shoulder_width=55.0,
            inseam=90.0,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            assert fitting.fit_result == "Loose"

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_user_cannot_use_another_users_avatar():
    """
    Verify that a user cannot use another user's avatar.
    """

    owner_email = "virtual.fitting.service.owner@example.com"
    other_email = "virtual.fitting.service.other@example.com"
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

        avatar = create_test_avatar(owner)

        garment = create_test_garment(
            user=other_user,
        )

        db = SessionLocal()

        try:
            try:
                create_virtual_fitting(
                    db=db,
                    user_id=other_user.user_id,
                    avatar_id=avatar.avatar_id,
                    garment_id=garment.garment_id,
                )

                assert False, (
                    "Expected unauthorized avatar "
                    "access to raise ValueError."
                )

            except ValueError as exc:
                assert str(exc) == "Avatar not found."

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)


def test_virtual_fitting_requires_valid_garment():
    """
    Verify that virtual fitting creation rejects a nonexistent
    garment.
    """

    email = "virtual.fitting.service.garment@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        db = SessionLocal()

        try:
            try:
                create_virtual_fitting(
                    db=db,
                    user_id=user.user_id,
                    avatar_id=avatar.avatar_id,
                    garment_id=uuid.uuid4(),
                )

                assert False, (
                    "Expected invalid garment "
                    "to raise ValueError."
                )

            except ValueError as exc:
                assert str(exc) == "Garment not found."

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_duplicate_virtual_fitting_is_rejected():
    """
    Verify that the same user, avatar, and garment cannot
    create duplicate virtual fittings.
    """

    email = "virtual.fitting.service.duplicate@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        db = SessionLocal()

        try:
            first_fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            assert first_fitting is not None

            try:
                create_virtual_fitting(
                    db=db,
                    user_id=user.user_id,
                    avatar_id=avatar.avatar_id,
                    garment_id=garment.garment_id,
                )

                assert False, (
                    "Expected duplicate virtual fitting "
                    "creation to raise ValueError."
                )

            except ValueError as exc:
                assert str(exc) == (
                    "A virtual fitting already exists "
                    "for this avatar and garment."
                )

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_get_virtual_fitting_by_id():
    """
    Verify that a user can retrieve their own virtual fitting.
    """

    email = "virtual.fitting.service.get@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=user.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            retrieved = get_virtual_fitting_by_id(
                db=db,
                fitting_id=fitting.fitting_id,
                user_id=user.user_id,
            )

            assert retrieved is not None

            assert (
                retrieved.fitting_id
                == fitting.fitting_id
            )

            assert (
                retrieved.user_id
                == user.user_id
            )

            assert (
                retrieved.avatar_id
                == avatar.avatar_id
            )

            assert (
                retrieved.garment_id
                == garment.garment_id
            )

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_user_cannot_retrieve_another_users_fitting():
    """
    Verify that a user cannot retrieve another user's fitting.
    """

    owner_email = "virtual.fitting.service.get.owner@example.com"
    viewer_email = "virtual.fitting.service.get.viewer@example.com"
    password = "SecurePassword123"

    delete_test_user(owner_email)
    delete_test_user(viewer_email)

    try:
        owner = create_test_user(
            email=owner_email,
            password=password,
        )

        viewer = create_test_user(
            email=viewer_email,
            password=password,
        )

        avatar = create_test_avatar(owner)

        garment = create_test_garment(
            user=owner,
        )

        db = SessionLocal()

        try:
            fitting = create_virtual_fitting(
                db=db,
                user_id=owner.user_id,
                avatar_id=avatar.avatar_id,
                garment_id=garment.garment_id,
            )

            retrieved = get_virtual_fitting_by_id(
                db=db,
                fitting_id=fitting.fitting_id,
                user_id=viewer.user_id,
            )

            assert retrieved is None

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(viewer_email)