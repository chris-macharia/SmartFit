"""
Database persistence tests for the SmartFit BodyMeasurement model.

This module verifies that a BodyMeasurement record can be:

1. Created and inserted into PostgreSQL.
2. Retrieved from the database.
3. Deleted after the test completes.

The test uses a temporary record so that it does not leave
unnecessary test data in the development database.
"""

import uuid

from app.db.database import SessionLocal
from app.models import BodyMeasurement


def test_create_and_retrieve_body_measurement():
    """
    Verify that a BodyMeasurement record can be created
    and retrieved from PostgreSQL.

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist body
    measurement data in the SmartFit database.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    # Generate a temporary UUID to represent the video
    # associated with this test measurement.
    #
    # The Video relationship will be refined later when the
    # database relationships are finalized.
    test_video_id = uuid.uuid4()

    try:
        # Create a temporary BodyMeasurement object.
        #
        # The values represent example body measurements
        # that could have been estimated by the SmartFit
        # computer vision processing module.
        test_measurement = BodyMeasurement(
            video_id=test_video_id,
            height=175.5,
            chest=100.0,
            waist=85.0,
            hips=98.0,
            shoulder_width=45.0,
            inseam=80.0,
        )

        # Add the BodyMeasurement object to the current
        # database session.
        db.add(test_measurement)

        # Commit the transaction so that the measurement record
        # is written to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves
        # database-generated values such as the measurement UUID.
        db.refresh(test_measurement)

        # Confirm that PostgreSQL generated a UUID for the
        # body measurement record.
        assert test_measurement.measurement_id is not None

        # Retrieve the BodyMeasurement record from PostgreSQL
        # using the generated measurement UUID.
        retrieved_measurement = db.query(BodyMeasurement).filter(
            BodyMeasurement.measurement_id
            == test_measurement.measurement_id
        ).first()

        # Confirm that the BodyMeasurement record was
        # successfully retrieved.
        assert retrieved_measurement is not None

        # Verify that the retrieved video ID matches the
        # video ID used to create the test measurement.
        assert retrieved_measurement.video_id == test_video_id

        # Verify that all measurement values were correctly
        # stored and retrieved from PostgreSQL.
        assert retrieved_measurement.height == 175.5
        assert retrieved_measurement.chest == 100.0
        assert retrieved_measurement.waist == 85.0
        assert retrieved_measurement.hips == 98.0
        assert retrieved_measurement.shoulder_width == 45.0
        assert retrieved_measurement.inseam == 80.0

    finally:
        # Remove the temporary test record from the database.
        #
        # This ensures that running the test does not leave
        # unnecessary test data in the SmartFit database.
        if (
            "test_measurement" in locals()
            and test_measurement.measurement_id is not None
        ):
            db.delete(test_measurement)
            db.commit()

        # Close the database session.
        db.close()