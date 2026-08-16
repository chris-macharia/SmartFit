"""
Tests for the SmartFit Video API.

This module tests video upload functionality for authenticated
and unauthenticated users.

The tests verify that:

1. Authenticated users can upload supported video files.
2. Unauthenticated users cannot upload videos.
3. Authenticated users cannot upload unsupported file types.
4. Test data and uploaded files are cleaned up after each test.
"""

from pathlib import Path

from app.db.database import SessionLocal
from app.models.user import User
from app.models.video import Video
from app.core.security import hash_password

from fastapi.testclient import TestClient

from app.main import app


# ============================================================
# Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Test Helper Functions
# ============================================================

def create_test_user(email: str, password: str):
    """
    Create a test user in the database.

    Args:
        email:
            Email address for the test user.

        password:
            Plain-text password which will be hashed before
            being stored in the database.

    Returns:
        User:
            The newly created test user.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Video Test User",
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


def delete_user_by_email(email: str):
    """
    Delete a test user and all associated test videos.

    Physical video files are removed before the database
    records are deleted.

    The User model defines a cascade relationship with Video,
    so deleting the user also deletes associated Video records.
    """

    db = SessionLocal()

    try:
        # Find the test user.
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user:
            # Remove the physical video files associated
            # with this user.
            for video in user.videos:
                video_path = Path(video.video_path)

                if video_path.exists():
                    video_path.unlink()

            # Delete the user.
            #
            # Because User.videos uses:
            #
            #     cascade="all, delete-orphan"
            #
            # SQLAlchemy will also delete the associated
            # Video database records.
            db.delete(user)

            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# Test 1
# ============================================================

def test_authenticated_user_can_upload_video():
    """
    Verify that an authenticated user can successfully
    upload a supported video file.
    """

    email = "video.upload@example.com"
    password = "SecurePassword123"

    # Remove any leftover data from a previous test run.
    delete_user_by_email(email)

    try:
        # ----------------------------------------------------
        # Create test user.
        # ----------------------------------------------------

        create_test_user(
            email=email,
            password=password,
        )

        # ----------------------------------------------------
        # Log in to obtain a JWT access token.
        # ----------------------------------------------------

        login_response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # ----------------------------------------------------
        # Upload a supported MP4 video.
        # ----------------------------------------------------

        response = client.post(
            "/api/videos/",
            headers={
                "Authorization": f"Bearer {token}",
            },
            files={
                "file": (
                    "body_video.mp4",
                    b"fake video content",
                    "video/mp4",
                )
            },
        )

        # ----------------------------------------------------
        # Verify successful upload.
        # ----------------------------------------------------

        assert response.status_code == 201

        data = response.json()

        assert "video_id" in data
        assert data["processing_status"] == "uploaded"

        assert data["video_path"] is not None

        # ----------------------------------------------------
        # Verify the database record.
        # ----------------------------------------------------

        db = SessionLocal()

        try:
            video = (
                db.query(Video)
                .filter(
                    Video.video_id == data["video_id"]
                )
                .first()
            )

            assert video is not None
            assert video.user_id is not None
            assert video.processing_status == "uploaded"

        finally:
            db.close()

    finally:
        # Clean up the test user, video record, and
        # physical video file.
        delete_user_by_email(email)


# ============================================================
# Test 2
# ============================================================

def test_unauthenticated_user_cannot_upload_video():
    """
    Verify that a user without a valid JWT cannot upload
    a video.
    """

    response = client.post(
        "/api/videos/",
        files={
            "file": (
                "body_video.mp4",
                b"fake video content",
                "video/mp4",
            )
        },
    )

    # Authentication is required.
    assert response.status_code == 401


# ============================================================
# Test 3
# ============================================================

def test_authenticated_user_cannot_upload_unsupported_file():
    """
    Verify that an authenticated user cannot upload a file
    whose MIME type is not supported by SmartFit.
    """

    email = "video.invalid.type@example.com"
    password = "SecurePassword123"

    # Remove any leftover data from a previous test run.
    delete_user_by_email(email)

    try:
        # ----------------------------------------------------
        # Create test user.
        # ----------------------------------------------------

        create_test_user(
            email=email,
            password=password,
        )

        # ----------------------------------------------------
        # Log in to obtain a JWT access token.
        # ----------------------------------------------------

        login_response = client.post(
            "/api/users/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        # ----------------------------------------------------
        # Attempt to upload an unsupported file type.
        # ----------------------------------------------------

        response = client.post(
            "/api/videos/",
            headers={
                "Authorization": f"Bearer {token}",
            },
            files={
                "file": (
                    "test.txt",
                    b"This is not a video.",
                    "text/plain",
                )
            },
        )

        # ----------------------------------------------------
        # Verify that the API rejects the file.
        # ----------------------------------------------------

        assert response.status_code == 400

        assert (
            response.json()["detail"]
            == (
                "Unsupported video format. "
                "Please upload an MP4, MOV, or WebM video."
            )
        )

    finally:
        # Clean up the test user and any associated data.
        delete_user_by_email(email)