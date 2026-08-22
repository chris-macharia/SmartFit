"""
Tests for the SmartFit Avatar API.

This module tests avatar generation and retrieval for authenticated
users.

The tests verify:

1. Authenticated users can generate avatars from their measurements.
2. Unauthenticated users cannot generate avatars.
3. Users cannot generate avatars from another user's measurements.
4. Authenticated users can retrieve their own avatars.
5. Unauthenticated users cannot retrieve avatars.
6. Non-existent avatar requests return 404.
7. Users cannot retrieve another user's avatar.
8. A measurement cannot generate duplicate avatars.
"""

import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.db.database import SessionLocal
from app.main import app
from app.models.avatar import Avatar
from app.models.body_measurements import BodyMeasurement
from app.models.user import User
from app.models.video import Video


# ============================================================
# Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Test Helpers
# ============================================================


def create_test_user(
    email: str,
    password: str,
):
    """Create a test user."""

    db = SessionLocal()

    try:
        user = User(
            full_name="Avatar API Test User",
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


def create_test_measurement(
    user: User,
):
    """
    Create a completed video and body measurement for a user.
    """

    db = SessionLocal()

    try:
        video = Video(
            user_id=user.user_id,
            video_path="uploads/videos/avatar-api-test.mp4",
            processing_status="completed",
            user_height_cm=175.0,
            processing_error=None,
        )

        db.add(video)
        db.flush()

        measurement = BodyMeasurement(
            video_id=video.video_id,
            height=175.0,
            shoulder_width=64.89,
            inseam=90.23,
            chest=None,
            waist=None,
            hips=None,
            confidence_score=0.96,
            processing_version="pose-v1",
        )

        db.add(measurement)
        db.commit()
        db.refresh(measurement)

        return measurement

    finally:
        db.close()


def delete_test_user(email: str):
    """
    Delete all avatar-related test data belonging to a user.
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

        videos = list(user.videos)

        for video in videos:

            measurements = (
                db.query(BodyMeasurement)
                .filter(
                    BodyMeasurement.video_id
                    == video.video_id
                )
                .all()
            )

            for measurement in measurements:

                avatars = (
                    db.query(Avatar)
                    .filter(
                        Avatar.measurement_id
                        == measurement.measurement_id
                    )
                    .all()
                )

                for avatar in avatars:
                    avatar_path = Path(
                        avatar.avatar_path
                    )

                    if avatar_path.exists():
                        avatar_path.unlink()

                    db.delete(avatar)

                db.delete(measurement)

        db.flush()

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def create_token(user: User) -> str:
    """Create an access token for a test user."""

    return create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )


# ============================================================
# CREATE AVATAR TESTS
# ============================================================


def test_authenticated_user_can_generate_avatar():
    """
    Verify that an authenticated user can generate an avatar
    from their completed body measurement.
    """

    email = "avatar.api.create@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        measurement = create_test_measurement(
            user
        )

        token = create_token(user)

        response = client.post(
            "/api/avatars/",
            params={
                "measurement_id": str(
                    measurement.measurement_id
                )
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert "avatar_id" in data
        assert (
            data["measurement_id"]
            == str(measurement.measurement_id)
        )
        assert data["avatar_path"].endswith(".glb")
        assert "created_at" in data

        # Verify the physical file exists.
        avatar_path = Path(
            data["avatar_path"]
        )

        assert avatar_path.exists()
        assert avatar_path.stat().st_size > 0

    finally:
        delete_test_user(email)


def test_unauthenticated_user_cannot_generate_avatar():
    """
    Verify that avatar generation requires authentication.
    """

    response = client.post(
        "/api/avatars/",
        params={
            "measurement_id": str(
                uuid.uuid4()
            )
        },
    )

    assert response.status_code == 401


def test_user_cannot_generate_avatar_from_another_users_measurement():
    """
    Verify that a user cannot generate an avatar from another
    user's body measurement.
    """

    owner_email = "avatar.api.owner@example.com"
    other_email = "avatar.api.other@example.com"
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

        measurement = create_test_measurement(
            owner
        )

        token = create_token(other_user)

        response = client.post(
            "/api/avatars/",
            params={
                "measurement_id": str(
                    measurement.measurement_id
                )
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 404
        assert (
            response.json()["detail"]
            == "Body measurement not found."
        )

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)


def test_duplicate_avatar_generation_returns_409():
    """
    Verify that generating an avatar twice from the same
    measurement returns HTTP 409.
    """

    email = "avatar.api.duplicate@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        measurement = create_test_measurement(
            user
        )

        token = create_token(user)

        headers = {
            "Authorization": f"Bearer {token}",
        }

        params = {
            "measurement_id": str(
                measurement.measurement_id
            )
        }

        first_response = client.post(
            "/api/avatars/",
            params=params,
            headers=headers,
        )

        assert first_response.status_code == 201

        second_response = client.post(
            "/api/avatars/",
            params=params,
            headers=headers,
        )

        assert second_response.status_code == 409

        assert (
            second_response.json()["detail"]
            == (
                "An avatar already exists for "
                "this body measurement."
            )
        )

    finally:
        delete_test_user(email)


# ============================================================
# GET AVATAR TESTS
# ============================================================


def test_authenticated_user_can_get_own_avatar():
    """
    Verify that an authenticated user can retrieve their
    generated avatar.
    """

    email = "avatar.api.get@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        measurement = create_test_measurement(
            user
        )

        token = create_token(user)

        headers = {
            "Authorization": f"Bearer {token}",
        }

        create_response = client.post(
            "/api/avatars/",
            params={
                "measurement_id": str(
                    measurement.measurement_id
                )
            },
            headers=headers,
        )

        assert create_response.status_code == 201

        avatar_id = create_response.json()["avatar_id"]

        response = client.get(
            f"/api/avatars/{avatar_id}",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["avatar_id"] == avatar_id
        assert (
            data["measurement_id"]
            == str(measurement.measurement_id)
        )
        assert data["avatar_path"].endswith(".glb")
        assert "created_at" in data

    finally:
        delete_test_user(email)


def test_unauthenticated_user_cannot_get_avatar():
    """
    Verify that retrieving an avatar requires authentication.
    """

    fake_avatar_id = uuid.uuid4()

    response = client.get(
        f"/api/avatars/{fake_avatar_id}",
    )

    assert response.status_code == 401


def test_get_nonexistent_avatar_returns_404():
    """
    Verify that requesting a nonexistent avatar returns 404.
    """

    email = "avatar.api.nonexistent@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        token = create_token(user)

        response = client.get(
            f"/api/avatars/{uuid.uuid4()}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Avatar not found."
        )

    finally:
        delete_test_user(email)


def test_user_cannot_get_another_users_avatar():
    """
    Verify that an authenticated user cannot retrieve another
    user's avatar.
    """

    owner_email = "avatar.api.get.owner@example.com"
    viewer_email = "avatar.api.get.viewer@example.com"
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

        measurement = create_test_measurement(
            owner
        )

        owner_token = create_token(owner)

        create_response = client.post(
            "/api/avatars/",
            params={
                "measurement_id": str(
                    measurement.measurement_id
                )
            },
            headers={
                "Authorization": f"Bearer {owner_token}",
            },
        )

        assert create_response.status_code == 201

        avatar_id = create_response.json()["avatar_id"]

        viewer_token = create_token(viewer)

        response = client.get(
            f"/api/avatars/{avatar_id}",
            headers={
                "Authorization": f"Bearer {viewer_token}",
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Avatar not found."
        )

    finally:
        delete_test_user(owner_email)
        delete_test_user(viewer_email)