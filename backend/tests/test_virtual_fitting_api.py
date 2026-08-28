"""
Tests for the SmartFit Virtual Fitting API.

This module tests virtual fitting creation and retrieval for
authenticated users.

The tests verify:

1. Authenticated users can create virtual fittings.
2. Unauthenticated users cannot create virtual fittings.
3. Users cannot use another user's avatar.
4. Invalid garments return 404.
5. Duplicate virtual fittings return 409.
6. Authenticated users can retrieve their own fitting.
7. Unauthenticated users cannot retrieve fittings.
8. Nonexistent fittings return 404.
9. Users cannot retrieve another user's fitting.
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
from app.models import (
    Avatar,
    BodyMeasurement,
    Garment,
    User,
    Video,
    VirtualFitting,
)


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
    role: str = "customer",
):
    """
    Create a temporary test user.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Virtual Fitting API Test User",
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def create_test_avatar(
    user: User,
):
    """
    Create a completed video, body measurement, and avatar
    for API testing.
    """

    db = SessionLocal()

    try:
        video = Video(
            user_id=user.user_id,
            video_path="uploads/videos/virtual-fitting-api-test.mp4",
            processing_status="completed",
            user_height_cm=175.0,
            processing_error=None,
        )

        db.add(video)
        db.flush()

        measurement = BodyMeasurement(
            video_id=video.video_id,
            height=175.0,
            chest=95.0,
            waist=80.0,
            hips=95.0,
            shoulder_width=45.0,
            inseam=80.0,
            confidence_score=0.96,
            processing_version="pose-v1",
        )

        db.add(measurement)
        db.flush()

        avatar = Avatar(
            measurement_id=measurement.measurement_id,
            avatar_path=(
                "uploads/avatars/"
                "virtual-fitting-api-test-avatar.glb"
            ),
        )

        db.add(avatar)
        db.commit()
        db.refresh(avatar)

        return avatar

    finally:
        db.close()


def create_test_garment(
    user: User,
    chest_width: float = 95.0,
    waist_width: float = 80.0,
    hip_width: float = 95.0,
    shoulder_width: float = 45.0,
    inseam: float = 80.0,
):
    """
    Create a temporary garment for API testing.
    """

    db = SessionLocal()

    try:
        garment = Garment(
            user_id=user.user_id,
            chest_width=chest_width,
            waist_width=waist_width,
            hip_width=hip_width,
            shoulder_width=shoulder_width,
            inseam=inseam,
        )

        db.add(garment)
        db.commit()
        db.refresh(garment)

        return garment

    finally:
        db.close()


def create_token(user: User) -> str:
    """
    Create an access token for a test user.
    """

    return create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )


def delete_test_user(email: str):
    """
    Delete all test data belonging to a user.

    VirtualFitting records are explicitly removed first because
    VirtualFitting currently does not define SQLAlchemy ORM
    relationships with cascade behavior.

    Video -> BodyMeasurement -> Avatar records are then removed
    automatically through the configured SQLAlchemy cascades when
    the User is deleted.

    Generated avatar files are removed from disk before the
    database records are deleted.
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

        # --------------------------------------------------------
        # Remove physical avatar files.
        # --------------------------------------------------------

        for video in list(user.videos):
            measurement = video.measurement

            if measurement is None:
                continue

            avatar = measurement.avatar

            if avatar is None:
                continue

            avatar_path = Path(avatar.avatar_path)

            if avatar_path.exists():
                avatar_path.unlink()

        # --------------------------------------------------------
        # Delete VirtualFitting records first.
        # --------------------------------------------------------
        #
        # VirtualFitting has foreign keys to User, Garment,
        # and Avatar but does not currently define ORM
        # cascade relationships.

        db.query(VirtualFitting).filter(
            VirtualFitting.user_id == user.user_id
        ).delete(
            synchronize_session=False
        )

        # --------------------------------------------------------
        # Delete the User.
        # --------------------------------------------------------
        #
        # SQLAlchemy cascades handle:
        #
        # User
        #   ├── Videos
        #   │     └── BodyMeasurements
        #   │           └── Avatars
        #   │
        #   └── Garments

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# CREATE VIRTUAL FITTING TESTS
# ============================================================


def test_authenticated_user_can_create_virtual_fitting():
    """
    Verify that an authenticated user can create a virtual
    fitting using their avatar and garment.
    """

    email = "virtual.fitting.api.create@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        token = create_token(user)

        response = client.post(
            "/api/virtual-fittings/",
            json={
                "avatar_id": str(
                    avatar.avatar_id
                ),
                "garment_id": str(
                    garment.garment_id
                ),
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert "fitting_id" in data

        assert (
            data["user_id"]
            == str(user.user_id)
        )

        assert (
            data["avatar_id"]
            == str(avatar.avatar_id)
        )

        assert (
            data["garment_id"]
            == str(garment.garment_id)
        )

        assert data["recommended_size"] is not None
        assert data["fit_result"] is not None
        assert "created_at" in data

    finally:
        delete_test_user(email)


def test_unauthenticated_user_cannot_create_virtual_fitting():
    """
    Verify that virtual fitting creation requires authentication.
    """

    response = client.post(
        "/api/virtual-fittings/",
        json={
            "avatar_id": str(uuid.uuid4()),
            "garment_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 401


def test_user_cannot_use_another_users_avatar():
    """
    Verify that a user cannot create a fitting using another
    user's avatar.
    """

    owner_email = "virtual.fitting.api.owner@example.com"
    other_email = "virtual.fitting.api.other@example.com"
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

        avatar = create_test_avatar(owner)

        garment = create_test_garment(
            user=other_user,
        )

        token = create_token(other_user)

        response = client.post(
            "/api/virtual-fittings/",
            json={
                "avatar_id": str(
                    avatar.avatar_id
                ),
                "garment_id": str(
                    garment.garment_id
                ),
            },
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
        delete_test_user(owner_email)
        delete_test_user(other_email)


def test_invalid_garment_returns_404():
    """
    Verify that using a nonexistent garment returns 404.
    """

    email = "virtual.fitting.api.garment@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        token = create_token(user)

        response = client.post(
            "/api/virtual-fittings/",
            json={
                "avatar_id": str(
                    avatar.avatar_id
                ),
                "garment_id": str(
                    uuid.uuid4()
                ),
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Garment not found."
        )

    finally:
        delete_test_user(email)


def test_duplicate_virtual_fitting_returns_409():
    """
    Verify that creating the same virtual fitting twice
    returns HTTP 409.
    """

    email = "virtual.fitting.api.duplicate@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        token = create_token(user)

        headers = {
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "avatar_id": str(
                avatar.avatar_id
            ),
            "garment_id": str(
                garment.garment_id
            ),
        }

        first_response = client.post(
            "/api/virtual-fittings/",
            json=payload,
            headers=headers,
        )

        assert first_response.status_code == 201

        second_response = client.post(
            "/api/virtual-fittings/",
            json=payload,
            headers=headers,
        )

        assert second_response.status_code == 409

        assert (
            second_response.json()["detail"]
            == (
                "A virtual fitting already exists "
                "for this avatar and garment."
            )
        )

    finally:
        delete_test_user(email)


# ============================================================
# GET VIRTUAL FITTING TESTS
# ============================================================


def test_authenticated_user_can_get_own_virtual_fitting():
    """
    Verify that an authenticated user can retrieve their
    own virtual fitting.
    """

    email = "virtual.fitting.api.get@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        avatar = create_test_avatar(user)

        garment = create_test_garment(
            user=user,
        )

        token = create_token(user)

        create_response = client.post(
            "/api/virtual-fittings/",
            json={
                "avatar_id": str(
                    avatar.avatar_id
                ),
                "garment_id": str(
                    garment.garment_id
                ),
            },
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert create_response.status_code == 201

        fitting_id = create_response.json()["fitting_id"]

        response = client.get(
            f"/api/virtual-fittings/{fitting_id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert (
            data["fitting_id"]
            == fitting_id
        )

        assert (
            data["user_id"]
            == str(user.user_id)
        )

        assert (
            data["avatar_id"]
            == str(avatar.avatar_id)
        )

        assert (
            data["garment_id"]
            == str(garment.garment_id)
        )

        assert data["recommended_size"] is not None
        assert data["fit_result"] is not None

    finally:
        delete_test_user(email)


def test_unauthenticated_user_cannot_get_virtual_fitting():
    """
    Verify that retrieving a virtual fitting requires
    authentication.
    """

    response = client.get(
        f"/api/virtual-fittings/{uuid.uuid4()}",
    )

    assert response.status_code == 401


def test_nonexistent_virtual_fitting_returns_404():
    """
    Verify that requesting a nonexistent virtual fitting
    returns 404.
    """

    email = "virtual.fitting.api.nonexistent@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        token = create_token(user)

        response = client.get(
            f"/api/virtual-fittings/{uuid.uuid4()}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Virtual fitting not found."
        )

    finally:
        delete_test_user(email)


def test_user_cannot_retrieve_another_users_fitting():
    """
    Verify that a user cannot retrieve another user's
    virtual fitting.
    """

    owner_email = "virtual.fitting.api.get.owner@example.com"
    viewer_email = "virtual.fitting.api.get.viewer@example.com"
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

        avatar = create_test_avatar(owner)

        garment = create_test_garment(
            user=owner,
        )

        owner_token = create_token(owner)

        create_response = client.post(
            "/api/virtual-fittings/",
            json={
                "avatar_id": str(
                    avatar.avatar_id
                ),
                "garment_id": str(
                    garment.garment_id
                ),
            },
            headers={
                "Authorization": f"Bearer {owner_token}",
            },
        )

        assert create_response.status_code == 201

        fitting_id = create_response.json()["fitting_id"]

        viewer_token = create_token(viewer)

        response = client.get(
            f"/api/virtual-fittings/{fitting_id}",
            headers={
                "Authorization": f"Bearer {viewer_token}",
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Virtual fitting not found."
        )

    finally:
        delete_test_user(owner_email)
        delete_test_user(viewer_email)