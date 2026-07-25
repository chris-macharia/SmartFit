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

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary User.
        # ---------------------------------------------------------
        #
        # The User is required by both:
        #
        # 1. The Video that produces the body measurements.
        # 2. The VirtualFitting itself.
        test_user = User(
            full_name="Virtual Fitting Test User",
            email="virtual.fitting.test.user@smartfit.test",
            hashed_password="test_hashed_password",
            role="customer",
        )

        # Add the User to the database session.
        db.add(test_user)

        # Commit the User so PostgreSQL generates the UUID.
        db.commit()

        # Refresh the User to retrieve the generated user_id.
        db.refresh(test_user)

        # Confirm that the User received a UUID.
        assert test_user.user_id is not None
        assert isinstance(test_user.user_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 2: Create a temporary Video.
        # ---------------------------------------------------------
        #
        # The Video belongs to the User created above.
        test_video = Video(
            user_id=test_user.user_id,
            video_path="uploads/virtual_fitting_test_video.mp4",
            processing_status="completed",
        )

        # Add the Video to the database session.
        db.add(test_video)

        # Commit the Video to PostgreSQL.
        db.commit()

        # Refresh to retrieve the generated video_id.
        db.refresh(test_video)

        # Confirm that the Video received a UUID.
        assert test_video.video_id is not None
        assert isinstance(test_video.video_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 3: Create BodyMeasurements.
        # ---------------------------------------------------------
        #
        # The BodyMeasurement is produced from the Video.
        test_measurement = BodyMeasurement(
            video_id=test_video.video_id,
            height=175.0,
            chest=95.0,
            waist=80.0,
            hips=95.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        # Add the BodyMeasurement to the database session.
        db.add(test_measurement)

        # Commit the BodyMeasurement.
        db.commit()

        # Refresh to retrieve the generated measurement_id.
        db.refresh(test_measurement)

        # Confirm that the BodyMeasurement received a UUID.
        assert test_measurement.measurement_id is not None
        assert isinstance(test_measurement.measurement_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 4: Create an Avatar.
        # ---------------------------------------------------------
        #
        # The Avatar is generated from the BodyMeasurement.
        test_avatar = Avatar(
            measurement_id=test_measurement.measurement_id,
            avatar_path="uploads/virtual_fitting_test_avatar.glb",
        )

        # Add the Avatar to the database session.
        db.add(test_avatar)

        # Commit the Avatar.
        db.commit()

        # Refresh to retrieve the generated avatar_id.
        db.refresh(test_avatar)

        # Confirm that the Avatar received a UUID.
        assert test_avatar.avatar_id is not None
        assert isinstance(test_avatar.avatar_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 5: Create a temporary Garment.
        # ---------------------------------------------------------
        #
        # The Garment belongs to the User acting as the retailer.
        #
        # In this test, we reuse the same User record to keep the
        # test simple. In the actual application, the retailer and
        # customer would normally be separate User accounts.
        test_garment = Garment(
            retailer_id=test_user.user_id,
            name="Virtual Fitting Test T-Shirt",
            category="T-Shirt",
            brand="SmartFit Test Brand",
            size="M",
            chest=100.0,
            waist=90.0,
            hips=100.0,
            length=70.0,
            image_path="uploads/virtual_fitting_test_garment.jpg",
        )

        # Add the Garment to the database session.
        db.add(test_garment)

        # Commit the Garment.
        db.commit()

        # Refresh to retrieve the generated garment_id.
        db.refresh(test_garment)

        # Confirm that the Garment received a UUID.
        assert test_garment.garment_id is not None
        assert isinstance(test_garment.garment_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 6: Create a VirtualFitting.
        # ---------------------------------------------------------
        #
        # The VirtualFitting references:
        #
        # - The User performing the fitting.
        # - The Garment selected for fitting.
        # - The Avatar used for the fitting.
        test_fitting = VirtualFitting(
            user_id=test_user.user_id,
            garment_id=test_garment.garment_id,
            avatar_id=test_avatar.avatar_id,
            recommended_size="M",
            fit_result="Good Fit",
        )

        # Add the VirtualFitting to the database session.
        db.add(test_fitting)

        # Commit the VirtualFitting to PostgreSQL.
        db.commit()

        # Refresh to retrieve the generated fitting_id.
        db.refresh(test_fitting)

        # Confirm that the VirtualFitting received a UUID.
        assert test_fitting.fitting_id is not None
        assert isinstance(test_fitting.fitting_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 7: Retrieve the VirtualFitting.
        # ---------------------------------------------------------

        retrieved_fitting = db.query(VirtualFitting).filter(
            VirtualFitting.fitting_id == test_fitting.fitting_id
        ).first()

        # Confirm that the VirtualFitting was successfully retrieved.
        assert retrieved_fitting is not None

        # Confirm that all foreign-key relationships are correct.
        assert retrieved_fitting.user_id == test_user.user_id
        assert retrieved_fitting.garment_id == test_garment.garment_id
        assert retrieved_fitting.avatar_id == test_avatar.avatar_id

        # Verify the VirtualFitting result data.
        assert retrieved_fitting.recommended_size == "M"
        assert retrieved_fitting.fit_result == "Good Fit"

        # Confirm that the creation timestamp was generated.
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

        # Delete the VirtualFitting first.
        if (
            "test_fitting" in locals()
            and test_fitting.fitting_id is not None
        ):
            db.delete(test_fitting)
            db.commit()

        # Delete the Garment.
        if (
            "test_garment" in locals()
            and test_garment.garment_id is not None
        ):
            db.delete(test_garment)
            db.commit()

        # Delete the Avatar.
        if (
            "test_avatar" in locals()
            and test_avatar.avatar_id is not None
        ):
            db.delete(test_avatar)
            db.commit()

        # Delete the BodyMeasurement.
        if (
            "test_measurement" in locals()
            and test_measurement.measurement_id is not None
        ):
            db.delete(test_measurement)
            db.commit()

        # Delete the Video.
        if (
            "test_video" in locals()
            and test_video.video_id is not None
        ):
            db.delete(test_video)
            db.commit()

        # Delete the User.
        if (
            "test_user" in locals()
            and test_user.user_id is not None
        ):
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()