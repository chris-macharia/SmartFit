"""
Database persistence tests for the SmartFit Avatar model.

This module verifies that an Avatar can be created and retrieved
using a valid BodyMeasurement foreign key.

The test also verifies that:

1. An Avatar receives a UUID primary key.
2. The Avatar correctly references its BodyMeasurement.
3. The one-to-one BodyMeasurement-to-Avatar relationship is respected.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Avatar, BodyMeasurement, User, Video


def test_create_and_retrieve_avatar():
    """
    Verify that an Avatar can be created and retrieved using
    a valid BodyMeasurement foreign key.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary User.
        # ---------------------------------------------------------
        #
        # The User is required because the Video belongs to a User.
        test_user = User(
            full_name="Avatar Test User",
            email="avatar.test.user@smartfit.test",
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
        # The Video references the User created above.
        test_video = Video(
            user_id=test_user.user_id,
            video_path="uploads/avatar_test_video.mp4",
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
        # Step 3: Create a BodyMeasurement.
        # ---------------------------------------------------------
        #
        # The BodyMeasurement references the Video created above.
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
        # The Avatar references the actual BodyMeasurement UUID.
        test_avatar = Avatar(
            measurement_id=test_measurement.measurement_id,
            avatar_path="uploads/test_avatar.glb",
        )

        # Add the Avatar to the database session.
        db.add(test_avatar)

        # Commit the Avatar to PostgreSQL.
        db.commit()

        # Refresh to retrieve the generated avatar_id.
        db.refresh(test_avatar)

        # Confirm that the Avatar received a UUID.
        assert test_avatar.avatar_id is not None
        assert isinstance(test_avatar.avatar_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 5: Retrieve the Avatar.
        # ---------------------------------------------------------

        retrieved_avatar = db.query(Avatar).filter(
            Avatar.avatar_id == test_avatar.avatar_id
        ).first()

        # Confirm that the Avatar was successfully retrieved.
        assert retrieved_avatar is not None

        # Confirm that the Avatar references the correct
        # BodyMeasurement.
        assert (
            retrieved_avatar.measurement_id
            == test_measurement.measurement_id
        )

        # Verify the Avatar path.
        assert retrieved_avatar.avatar_path == "uploads/test_avatar.glb"

        # Confirm that the creation timestamp was generated.
        assert retrieved_avatar.created_at is not None

    finally:
        # ---------------------------------------------------------
        # Step 6: Clean up test data.
        # ---------------------------------------------------------
        #
        # Delete records in reverse dependency order:
        #
        # Avatar
        #    ↓
        # BodyMeasurement
        #    ↓
        # Video
        #    ↓
        # User

        # Delete the Avatar first.
        if "test_avatar" in locals() and test_avatar.avatar_id is not None:
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
        if "test_video" in locals() and test_video.video_id is not None:
            db.delete(test_video)
            db.commit()

        # Delete the User.
        if "test_user" in locals() and test_user.user_id is not None:
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()