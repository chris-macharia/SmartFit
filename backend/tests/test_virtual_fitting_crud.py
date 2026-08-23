"""
Database persistence tests for the SmartFit VirtualFitting model.

This module verifies that a VirtualFitting can be created and
retrieved using valid foreign keys referencing:

1. A User.
2. A Garment.
3. An Avatar.

The test creates the complete dependency chain required by the
VirtualFitting entity before creating the VirtualFitting record.
"""

import uuid

from app.db.database import SessionLocal
from app.models import (
    Avatar,
    BodyMeasurement,
    Garment,
    User,
    Video,
    VirtualFitting,
)


def test_create_and_retrieve_virtual_fitting():
    """
    Verify that a VirtualFitting can be created and retrieved
    using valid User, Garment, and Avatar foreign keys.
    """

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary User.
        # ---------------------------------------------------------
        #
        # The User is required by:
        #
        # 1. The Video that produces the body measurements.
        # 2. The VirtualFitting itself.
        # 3. The Garment in this simplified test setup.
        #
        # We use a retailer role because Garments are registered
        # by retailers.

        test_user = User(
            full_name="Virtual Fitting Test User",
            email="virtual.fitting.test.user@smartfit.test",
            hashed_password="test_hashed_password",
            role="retailer",
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        assert test_user.user_id is not None
        assert isinstance(
            test_user.user_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 2: Create a temporary Video.
        # ---------------------------------------------------------

        test_video = Video(
            user_id=test_user.user_id,
            video_path="uploads/virtual_fitting_test_video.mp4",
            processing_status="completed",
        )

        db.add(test_video)
        db.commit()
        db.refresh(test_video)

        assert test_video.video_id is not None
        assert isinstance(
            test_video.video_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 3: Create BodyMeasurement.
        # ---------------------------------------------------------

        test_measurement = BodyMeasurement(
            video_id=test_video.video_id,
            height=175.0,
            chest=95.0,
            waist=80.0,
            hips=95.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        db.add(test_measurement)
        db.commit()
        db.refresh(test_measurement)

        assert test_measurement.measurement_id is not None
        assert isinstance(
            test_measurement.measurement_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 4: Create an Avatar.
        # ---------------------------------------------------------

        test_avatar = Avatar(
            measurement_id=test_measurement.measurement_id,
            avatar_path=(
                "uploads/virtual_fitting_test_avatar.glb"
            ),
        )

        db.add(test_avatar)
        db.commit()
        db.refresh(test_avatar)

        assert test_avatar.avatar_id is not None
        assert isinstance(
            test_avatar.avatar_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 5: Create a temporary Garment.
        # ---------------------------------------------------------
        #
        # The current Garment model stores the uploader as
        # user_id.
        #
        # The User has the retailer role, so this represents
        # a retailer-registered garment.

        test_garment = Garment(
            user_id=test_user.user_id,
            chest_width=100.0,
            waist_width=90.0,
            hip_width=100.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        db.add(test_garment)
        db.commit()
        db.refresh(test_garment)

        assert test_garment.garment_id is not None
        assert isinstance(
            test_garment.garment_id,
            uuid.UUID,
        )

        # Confirm that the garment belongs to the test user.
        assert (
            test_garment.user_id
            == test_user.user_id
        )

        # ---------------------------------------------------------
        # Step 6: Create a VirtualFitting.
        # ---------------------------------------------------------

        test_fitting = VirtualFitting(
            user_id=test_user.user_id,
            garment_id=test_garment.garment_id,
            avatar_id=test_avatar.avatar_id,
            recommended_size="M",
            fit_result="Good Fit",
        )

        db.add(test_fitting)
        db.commit()
        db.refresh(test_fitting)

        assert test_fitting.fitting_id is not None
        assert isinstance(
            test_fitting.fitting_id,
            uuid.UUID,
        )

        # ---------------------------------------------------------
        # Step 7: Retrieve the VirtualFitting.
        # ---------------------------------------------------------

        retrieved_fitting = (
            db.query(VirtualFitting)
            .filter(
                VirtualFitting.fitting_id
                == test_fitting.fitting_id
            )
            .first()
        )

        assert retrieved_fitting is not None

        # Verify foreign-key relationships.
        assert (
            retrieved_fitting.user_id
            == test_user.user_id
        )

        assert (
            retrieved_fitting.garment_id
            == test_garment.garment_id
        )

        assert (
            retrieved_fitting.avatar_id
            == test_avatar.avatar_id
        )

        # Verify fitting result data.
        assert (
            retrieved_fitting.recommended_size
            == "M"
        )

        assert (
            retrieved_fitting.fit_result
            == "Good Fit"
        )

        # Confirm creation timestamp.
        assert retrieved_fitting.created_at is not None

    finally:
        # ---------------------------------------------------------
        # Step 8: Clean up test data.
        # ---------------------------------------------------------
        #
        # Delete records in reverse dependency order.
        #
        # VirtualFitting
        #       ↓
        # Garment
        #       ↓
        # Avatar
        #       ↓
        # BodyMeasurement
        #       ↓
        # Video
        #       ↓
        # User

        if (
            "test_fitting" in locals()
            and test_fitting.fitting_id is not None
        ):
            db.delete(test_fitting)
            db.commit()

        if (
            "test_garment" in locals()
            and test_garment.garment_id is not None
        ):
            db.delete(test_garment)
            db.commit()

        if (
            "test_avatar" in locals()
            and test_avatar.avatar_id is not None
        ):
            db.delete(test_avatar)
            db.commit()

        if (
            "test_measurement" in locals()
            and test_measurement.measurement_id is not None
        ):
            db.delete(test_measurement)
            db.commit()

        if (
            "test_video" in locals()
            and test_video.video_id is not None
        ):
            db.delete(test_video)
            db.commit()

        if (
            "test_user" in locals()
            and test_user.user_id is not None
        ):
            db.delete(test_user)
            db.commit()

        db.close()