"""
Database persistence tests for the SmartFit Video model.

This module verifies that a Video record can be:

1. Created using a valid User foreign key.
2. Inserted into PostgreSQL.
3. Retrieved from the database.
4. Deleted after the test completes.

The test also verifies that the Video correctly references
the User who uploaded it.
"""

import uuid

from app.db.database import SessionLocal
from app.models import User, Video


def test_create_and_retrieve_video():
    """
    Verify that a Video can be created and retrieved using
    a valid User foreign key.
    """

    # Create a new SQLAlchemy database session.
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Step 1: Create a temporary User.
        # ---------------------------------------------------------
        #
        # The User must exist before creating the Video because
        # videos.user_id is now a foreign key referencing users.user_id.
        test_user = User(
            full_name="Video Test User",
            email="video.test.user@smartfit.test",
            hashed_password="test_hashed_password",
            role="customer",
        )

        # Add the User to the database session.
        db.add(test_user)

        # Commit the User so that PostgreSQL generates the UUID
        # and the record becomes available for the foreign-key
        # relationship.
        db.commit()

        # Refresh the User to retrieve its generated UUID.
        db.refresh(test_user)

        # Confirm that the User received a UUID.
        assert test_user.user_id is not None
        assert isinstance(test_user.user_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 2: Create a temporary Video.
        # ---------------------------------------------------------
        #
        # The Video references the actual User UUID created above.
        test_video = Video(
            user_id=test_user.user_id,
            video_path="uploads/test_video.mp4",
            processing_status="pending",
        )

        # Add the Video to the database session.
        db.add(test_video)

        # Commit the Video to PostgreSQL.
        db.commit()

        # Refresh the Video to retrieve its generated values.
        db.refresh(test_video)

        # Confirm that the Video received a UUID primary key.
        assert test_video.video_id is not None
        assert isinstance(test_video.video_id, uuid.UUID)

        # ---------------------------------------------------------
        # Step 3: Retrieve the Video.
        # ---------------------------------------------------------

        # Retrieve the Video using its UUID primary key.
        retrieved_video = db.query(Video).filter(
            Video.video_id == test_video.video_id
        ).first()

        # Confirm that the Video was successfully retrieved.
        assert retrieved_video is not None

        # Confirm that the Video references the correct User.
        assert retrieved_video.user_id == test_user.user_id

        # Verify the remaining Video data.
        assert retrieved_video.video_path == "uploads/test_video.mp4"
        assert retrieved_video.processing_status == "pending"

        # Confirm that the upload timestamp was generated.
        assert retrieved_video.uploaded_at is not None

    finally:
        # ---------------------------------------------------------
        # Step 4: Clean up test data.
        # ---------------------------------------------------------
        #
        # The Video must be deleted before the User because the
        # Video contains a foreign key referencing the User.
        if "test_video" in locals() and test_video.video_id is not None:
            db.delete(test_video)
            db.commit()

        # Delete the temporary User.
        if "test_user" in locals() and test_user.user_id is not None:
            db.delete(test_user)
            db.commit()

        # Close the database session.
        db.close()