"""
Tests for the SmartFit Video API.

This module tests video creation/upload and deletion functionality
for authenticated and unauthenticated users.

The tests verify that:

1. Authenticated users can upload supported video files.
2. Unauthenticated users cannot upload videos.
3. Authenticated users cannot upload unsupported file types.
4. Authenticated users can delete their own videos.
5. Unauthenticated users cannot delete videos.
6. Authenticated users cannot delete another user's video.
7. Test data and uploaded files are cleaned up after each test.

SmartFit does not provide an update operation for videos.

If a user records or selects an incorrect video, the existing
video can be deleted and a new video can be uploaded instead.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.security import hash_password, create_access_token
from app.db.database import SessionLocal
from app.main import app
from app.models.user import User
from app.models.video import Video


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

    The supplied password is hashed before being stored.

    Args:
        email:
            Email address for the test user.

        password:
            Plain-text password used to create the test account.

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

    This helper makes the video API tests safe to run repeatedly
    without leftover test data affecting later tests.
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

            # Remove physical video files associated with
            # this test user.
            for video in user.videos:

                video_path = Path(video.video_path)

                if video_path.exists():
                    video_path.unlink()

            # Delete the user.
            #
            # The User -> Video relationship is configured with
            # cascade deletion, so the associated Video records
            # are also removed.
            db.delete(user)

            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# CREATE / UPLOAD VIDEO TESTS
# ============================================================


def test_authenticated_user_can_upload_video():
    """
    Verify that an authenticated user can successfully
    upload a supported video file.
    """

    email = "video.upload@example.com"
    password = "SecurePassword123"

    # Remove leftover data from previous test runs.
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
        # Remove the test user, video record and physical file.
        delete_user_by_email(email)


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


def test_authenticated_user_cannot_upload_unsupported_file():
    """
    Verify that an authenticated user cannot upload a file
    whose MIME type is not supported by SmartFit.
    """

    email = "video.invalid.type@example.com"
    password = "SecurePassword123"

    # Remove leftover data from previous test runs.
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
        # Remove the test user and associated data.
        delete_user_by_email(email)


# ============================================================
# DELETE VIDEO TESTS
# ============================================================


def test_authenticated_user_can_delete_video():
    """
    Verify that an authenticated user can delete their own
    video.

    The test creates a video record, creates its physical file,
    deletes the video through the API, and then verifies that
    both the database record and physical file are removed.
    """

    email = "video.delete@example.com"
    password = "SecurePassword123"

    # Remove leftover data from previous test runs.
    delete_user_by_email(email)

    try:
        # ----------------------------------------------------
        # Create test user.
        # ----------------------------------------------------

        user = create_test_user(
            email=email,
            password=password,
        )

        # ----------------------------------------------------
        # Generate an access token.
        # ----------------------------------------------------

        token = create_access_token(
            data={
                "sub": str(user.user_id),
            }
        )

        headers = {
            "Authorization": f"Bearer {token}",
        }

        # ----------------------------------------------------
        # Create a physical test video file.
        # ----------------------------------------------------

        video_path = Path(
            "uploads/videos/delete-test.mp4"
        )

        video_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        video_path.write_bytes(
            b"fake video content"
        )

        # ----------------------------------------------------
        # Create the database video record.
        # ----------------------------------------------------

        db = SessionLocal()

        try:
            video = Video(
                user_id=user.user_id,
                video_path=str(video_path),
                processing_status="uploaded",
            )

            db.add(video)
            db.commit()
            db.refresh(video)

            video_id = video.video_id

        finally:
            db.close()

        # ----------------------------------------------------
        # Delete the video through the API.
        # ----------------------------------------------------

        response = client.delete(
            f"/api/videos/{video_id}",
            headers=headers,
        )

        # ----------------------------------------------------
        # Verify successful deletion.
        # ----------------------------------------------------

        assert response.status_code == 204

        # ----------------------------------------------------
        # Verify that the database record was deleted.
        # ----------------------------------------------------

        db = SessionLocal()

        try:
            deleted_video = (
                db.query(Video)
                .filter(
                    Video.video_id == video_id
                )
                .first()
            )

            assert deleted_video is None

        finally:
            db.close()

        # ----------------------------------------------------
        # Verify that the physical file was deleted.
        # ----------------------------------------------------

        assert not video_path.exists()

    finally:
        # Clean up anything that may remain if the test fails.
        delete_user_by_email(email)

        # Also remove the test file if it still exists.
        video_path = Path(
            "uploads/videos/delete-test.mp4"
        )

        if video_path.exists():
            video_path.unlink()


def test_unauthenticated_user_cannot_delete_video():
    """
    Verify that a video cannot be deleted without authentication.
    """

    email = "video.delete.unauthenticated@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        # ----------------------------------------------------
        # Create test user.
        # ----------------------------------------------------

        user = create_test_user(
            email=email,
            password=password,
        )

        # ----------------------------------------------------
        # Create a physical test video file.
        # ----------------------------------------------------

        video_path = Path(
            "uploads/videos/delete-auth-test.mp4"
        )

        video_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        video_path.write_bytes(
            b"fake video content"
        )

        # ----------------------------------------------------
        # Create the database video record.
        # ----------------------------------------------------

        db = SessionLocal()

        try:
            video = Video(
                user_id=user.user_id,
                video_path=str(video_path),
                processing_status="uploaded",
            )

            db.add(video)
            db.commit()
            db.refresh(video)

            video_id = video.video_id

        finally:
            db.close()

        # ----------------------------------------------------
        # Attempt to delete without authentication.
        # ----------------------------------------------------

        response = client.delete(
            f"/api/videos/{video_id}",
        )

        # Authentication is required.
        assert response.status_code == 401

    finally:
        # Clean up the test data.
        delete_user_by_email(email)

        video_path = Path(
            "uploads/videos/delete-auth-test.mp4"
        )

        if video_path.exists():
            video_path.unlink()


def test_user_cannot_delete_another_users_video():
    """
    Verify that an authenticated user cannot delete a video
    belonging to another user.
    """

    owner_email = "video.delete.owner@example.com"
    other_email = "video.delete.other@example.com"
    password = "SecurePassword123"

    delete_user_by_email(owner_email)
    delete_user_by_email(other_email)

    try:
        # ----------------------------------------------------
        # Create the video owner.
        # ----------------------------------------------------

        owner = create_test_user(
            email=owner_email,
            password=password,
        )

        # ----------------------------------------------------
        # Create another user.
        # ----------------------------------------------------

        other_user = create_test_user(
            email=other_email,
            password=password,
        )

        # ----------------------------------------------------
        # Generate a token for the other user.
        # ----------------------------------------------------

        token = create_access_token(
            data={
                "sub": str(other_user.user_id),
            }
        )

        headers = {
            "Authorization": f"Bearer {token}",
        }

        # ----------------------------------------------------
        # Create a physical test video file belonging to
        # the owner.
        # ----------------------------------------------------

        video_path = Path(
            "uploads/videos/delete-owner-video.mp4"
        )

        video_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        video_path.write_bytes(
            b"fake video content"
        )

        # ----------------------------------------------------
        # Create the owner's video database record.
        # ----------------------------------------------------

        db = SessionLocal()

        try:
            video = Video(
                user_id=owner.user_id,
                video_path=str(video_path),
                processing_status="uploaded",
            )

            db.add(video)
            db.commit()
            db.refresh(video)

            video_id = video.video_id

        finally:
            db.close()

        # ----------------------------------------------------
        # Attempt to delete the owner's video using the
        # other user's authentication token.
        # ----------------------------------------------------

        response = client.delete(
            f"/api/videos/{video_id}",
            headers=headers,
        )

        # The API should not reveal another user's video.
        assert response.status_code == 404

    finally:
        # Clean up both test users.
        delete_user_by_email(owner_email)
        delete_user_by_email(other_email)

        # Remove the physical file if it still exists.
        video_path = Path(
            "uploads/videos/delete-owner-video.mp4"
        )

        if video_path.exists():
            video_path.unlink()