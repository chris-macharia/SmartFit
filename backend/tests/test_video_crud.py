"""
Database persistence tests for the SmartFit Video model.

This module verifies that a Video record can be:

1. Created and inserted into PostgreSQL.
2. Retrieved from the database.
3. Deleted after the test completes.

The test uses a temporary record so that it does not leave
unnecessary test data in the development database.
"""

import uuid

from app.db.database import SessionLocal
from app.models import Video


def test_create_and_retrieve_video():
    """
    Verify that a Video record can be created and retrieved.

    This test confirms that SQLAlchemy can successfully perform
    the basic database operations required to persist a Video
    record in PostgreSQL.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    # Generate a temporary UUID to represent the user
    # associated with this test video.
    #
    # The User relationship will be refined later when the
    # User database design is updated.
    test_user_id = uuid.uuid4()

    try:
        # Create a temporary Video object.
        #
        # The video_path represents the location where the uploaded
        # video would be stored by the SmartFit application.
        test_video = Video(
            user_id=test_user_id,
            video_path="uploads/test_body_video.mp4",
            processing_status="uploaded",
        )

        # Add the Video object to the current database session.
        db.add(test_video)

        # Commit the transaction so that the Video record is
        # written to the PostgreSQL database.
        db.commit()

        # Refresh the object so that SQLAlchemy retrieves
        # database-generated values such as the video UUID.
        db.refresh(test_video)

        # Confirm that PostgreSQL generated a UUID for the video.
        assert test_video.video_id is not None

        # Retrieve the Video record from PostgreSQL using
        # the generated video UUID.
        retrieved_video = db.query(Video).filter(
            Video.video_id == test_video.video_id
        ).first()

        # Confirm that the Video record was successfully retrieved.
        assert retrieved_video is not None

        # Verify that the retrieved information matches the
        # information used to create the test Video.
        assert retrieved_video.user_id == test_user_id
        assert retrieved_video.video_path == "uploads/test_body_video.mp4"
        assert retrieved_video.processing_status == "uploaded"

        # Confirm that the upload timestamp was automatically
        # generated when the Video record was created.
        assert retrieved_video.uploaded_at is not None

    finally:
        # Remove the temporary test record from the database.
        #
        # This ensures that running the test does not leave
        # unnecessary test data in the SmartFit database.
        if (
            "test_video" in locals()
            and test_video.video_id is not None
        ):
            db.delete(test_video)
            db.commit()

        # Close the database session.
        db.close()