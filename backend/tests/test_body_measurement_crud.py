"""
Database persistence tests for the SmartFit BodyMeasurement model.

This module verifies that a BodyMeasurement can be created and
retrieved using a valid Video foreign key.

The test also verifies that:

1. A BodyMeasurement receives a UUID primary key.
2. The measurement correctly references its source Video.
3. The one-to-one Video-to-BodyMeasurement relationship is respected.
"""

import uuid

from app.db.database import SessionLocal
from app.models import BodyMeasurement, User, Video


def test_create_and_retrieve_body_measurement():
    """
    Verify that a BodyMeasurement can be created and retrieved
    using a valid Video foreign key.
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
            full_name="Measurement Test User",
            email="measurement.test.user@smartfit.test",
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
            video_path="uploads/measurement_test_video.mp4",
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
        # The BodyMeasurement references the actual Video UUID.
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

        # Commit the measurement to PostgreSQL.
        db.commit()

        # Refresh to retrieve the generated measurement_id.
        db.refresh(test_measurement)

        # Confirm that the BodyMeasurement received a UUID.
        assert test_measurement.measurement_id is not None
        assert isinstance(test_measurement.measurement_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 4: Retrieve the BodyMeasurement.
        # ---------------------------------------------------------

        retrieved_measurement = db.query(BodyMeasurement).filter(
            BodyMeasurement.measurement_id
            == test_measurement.measurement_id
        ).first()

        # Confirm that the measurement was retrieved successfully.
        assert retrieved_measurement is not None

        # Confirm that the measurement references the correct Video.
        assert retrieved_measurement.video_id == test_video.video_id

        # Verify the measurement values.
        assert retrieved_measurement.height == 175.0
        assert retrieved_measurement.chest == 95.0
        assert retrieved_measurement.waist == 80.0
        assert retrieved_measurement.hips == 95.0
        assert retrieved_measurement.shoulder_width == 45.0
        assert retrieved_measurement.inseam == 80.0

    finally:
        # ---------------------------------------------------------
        # Step 5: Clean up test data.
        # ---------------------------------------------------------
        #
        # Delete records in reverse dependency order.
        #
        # BodyMeasurement references Video,
        # and Video references User.
        #
        # Therefore, BodyMeasurement must be deleted first.
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