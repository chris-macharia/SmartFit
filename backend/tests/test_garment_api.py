"""
Tests for the SmartFit Garment API.

This module tests garment creation, retrieval, updating, and deletion
for authenticated retailer users.

The tests verify that:

1. Authenticated retailers can create garments.
2. Unauthenticated users cannot create garments.
3. Non-retailer users cannot create garments.
4. Authenticated retailers can retrieve their garments.
5. Authenticated retailers can retrieve one of their garments.
6. Non-existent garments return 404.
7. Retailers cannot access another retailer's garment.
8. Authenticated retailers can update their garments.
9. Retailers cannot update another retailer's garment.
10. Authenticated retailers can delete their garments.
11. Retailers cannot delete another retailer's garment.
12. Unauthenticated users cannot access protected garment endpoints.
"""

import uuid

from fastapi.testclient import TestClient

from app.core.security import (
    create_access_token,
    hash_password,
)
from app.db.database import SessionLocal
from app.main import app
from app.models.garment import Garment
from app.models.user import User


# ============================================================
# Test Client
# ============================================================

client = TestClient(app)


# ============================================================
# Test Helper Functions
# ============================================================

def create_test_user(
    email: str,
    password: str,
    role: str,
):
    """
    Create a temporary test user.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Garment API Test User",
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


def delete_user_by_email(email: str):
    """
    Delete a temporary test user and all garments belonging
    to that user.
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

        garments = (
            db.query(Garment)
            .filter(
                Garment.user_id == user.user_id,
            )
            .all()
        )

        for garment in garments:
            db.delete(garment)

        db.flush()

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def create_garment_for_user(user_id: uuid.UUID):
    """
    Create a garment directly in the database for API retrieval,
    update, and delete tests.
    """

    db = SessionLocal()

    try:
        garment = Garment(
            garment_id=uuid.uuid4(),
            user_id=user_id,
            chest_width=50.0,
            waist_width=45.0,
            hip_width=52.0,
            shoulder_width=44.0,
            inseam=80.0,
        )

        db.add(garment)
        db.commit()
        db.refresh(garment)

        return garment

    finally:
        db.close()


def get_auth_headers(user: User):
    """
    Generate JWT authentication headers for a test user.
    """

    token = create_access_token(
        data={
            "sub": str(user.user_id),
        }
    )

    return {
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# CREATE - Garment
# ============================================================


def test_authenticated_retailer_can_create_garment():
    """
    Verify that an authenticated retailer can register a garment.
    """

    email = "garment.api.create@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        headers = get_auth_headers(user)

        response = client.post(
            "/api/garments/",
            headers=headers,
            json={
                "chest_width": 50.0,
                "waist_width": 45.0,
                "hip_width": 52.0,
                "shoulder_width": 44.0,
                "inseam": 80.0,
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert "garment_id" in data
        assert data["user_id"] == str(user.user_id)

        assert data["chest_width"] == 50.0
        assert data["waist_width"] == 45.0
        assert data["hip_width"] == 52.0
        assert data["shoulder_width"] == 44.0
        assert data["inseam"] == 80.0

        assert "created_at" in data

    finally:
        delete_user_by_email(email)


def test_unauthenticated_user_cannot_create_garment():
    """
    Verify that garment creation requires authentication.
    """

    response = client.post(
        "/api/garments/",
        json={
            "chest_width": 50.0,
            "waist_width": 45.0,
            "hip_width": 52.0,
            "shoulder_width": 44.0,
            "inseam": 80.0,
        },
    )

    assert response.status_code == 401


def test_customer_cannot_create_garment():
    """
    Verify that only retailer accounts can register garments.
    """

    email = "garment.api.customer.create@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="customer",
        )

        headers = get_auth_headers(user)

        response = client.post(
            "/api/garments/",
            headers=headers,
            json={
                "chest_width": 50.0,
                "waist_width": 45.0,
                "hip_width": 52.0,
                "shoulder_width": 44.0,
                "inseam": 80.0,
            },
        )

        assert response.status_code == 403

    finally:
        delete_user_by_email(email)


# ============================================================
# READ - Garments
# ============================================================


def test_authenticated_retailer_can_get_own_garments():
    """
    Verify that a retailer can retrieve their own garments.
    """

    email = "garment.api.list@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        create_garment_for_user(user.user_id)

        headers = get_auth_headers(user)

        response = client.get(
            "/api/garments/",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 1

        assert data[0]["user_id"] == str(
            user.user_id
        )

    finally:
        delete_user_by_email(email)


def test_authenticated_retailer_can_get_own_garment():
    """
    Verify that a retailer can retrieve a specific garment
    belonging to them.
    """

    email = "garment.api.get@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            user.user_id
        )

        headers = get_auth_headers(user)

        response = client.get(
            f"/api/garments/{garment.garment_id}",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["garment_id"] == str(
            garment.garment_id
        )

        assert data["user_id"] == str(
            user.user_id
        )

        assert data["chest_width"] == 50.0
        assert data["waist_width"] == 45.0
        assert data["hip_width"] == 52.0
        assert data["shoulder_width"] == 44.0
        assert data["inseam"] == 80.0

    finally:
        delete_user_by_email(email)


def test_get_nonexistent_garment_returns_404():
    """
    Verify that requesting a nonexistent garment returns 404.
    """

    email = "garment.api.notfound@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        headers = get_auth_headers(user)

        nonexistent_id = uuid.uuid4()

        response = client.get(
            f"/api/garments/{nonexistent_id}",
            headers=headers,
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Garment not found."
        )

    finally:
        delete_user_by_email(email)


def test_retailer_cannot_get_another_users_garment():
    """
    Verify that a retailer cannot retrieve another retailer's garment.
    """

    owner_email = "garment.api.owner@example.com"
    other_email = "garment.api.viewer@example.com"
    password = "SecurePassword123"

    delete_user_by_email(owner_email)
    delete_user_by_email(other_email)

    try:
        owner = create_test_user(
            email=owner_email,
            password=password,
            role="retailer",
        )

        other_user = create_test_user(
            email=other_email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            owner.user_id
        )

        headers = get_auth_headers(
            other_user
        )

        response = client.get(
            f"/api/garments/{garment.garment_id}",
            headers=headers,
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Garment not found."
        )

    finally:
        delete_user_by_email(owner_email)
        delete_user_by_email(other_email)


# ============================================================
# UPDATE - Garment
# ============================================================


def test_authenticated_retailer_can_update_own_garment():
    """
    Verify that a retailer can update their garment measurements.
    """

    email = "garment.api.update@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            user.user_id
        )

        headers = get_auth_headers(user)

        response = client.put(
            f"/api/garments/{garment.garment_id}",
            headers=headers,
            json={
                "chest_width": 55.0,
                "waist_width": 48.0,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["garment_id"] == str(
            garment.garment_id
        )

        assert data["chest_width"] == 55.0
        assert data["waist_width"] == 48.0

        # Fields not supplied in the update should remain unchanged.
        assert data["hip_width"] == 52.0
        assert data["shoulder_width"] == 44.0
        assert data["inseam"] == 80.0

    finally:
        delete_user_by_email(email)


def test_retailer_cannot_update_another_users_garment():
    """
    Verify that a retailer cannot update another retailer's garment.
    """

    owner_email = "garment.api.update.owner@example.com"
    other_email = "garment.api.update.other@example.com"
    password = "SecurePassword123"

    delete_user_by_email(owner_email)
    delete_user_by_email(other_email)

    try:
        owner = create_test_user(
            email=owner_email,
            password=password,
            role="retailer",
        )

        other_user = create_test_user(
            email=other_email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            owner.user_id
        )

        headers = get_auth_headers(
            other_user
        )

        response = client.put(
            f"/api/garments/{garment.garment_id}",
            headers=headers,
            json={
                "chest_width": 60.0,
            },
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Garment not found."
        )

    finally:
        delete_user_by_email(owner_email)
        delete_user_by_email(other_email)


# ============================================================
# DELETE - Garment
# ============================================================


def test_authenticated_retailer_can_delete_own_garment():
    """
    Verify that a retailer can delete their own garment.
    """

    email = "garment.api.delete@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            user.user_id
        )

        garment_id = garment.garment_id

        headers = get_auth_headers(user)

        response = client.delete(
            f"/api/garments/{garment_id}",
            headers=headers,
        )

        assert response.status_code == 204

        # Verify that the database record no longer exists.
        db = SessionLocal()

        try:
            deleted_garment = (
                db.query(Garment)
                .filter(
                    Garment.garment_id == garment_id
                )
                .first()
            )

            assert deleted_garment is None

        finally:
            db.close()

    finally:
        delete_user_by_email(email)


def test_unauthenticated_user_cannot_delete_garment():
    """
    Verify that garment deletion requires authentication.
    """

    email = "garment.api.delete.auth@example.com"
    password = "SecurePassword123"

    delete_user_by_email(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            user.user_id
        )

        response = client.delete(
            f"/api/garments/{garment.garment_id}",
        )

        assert response.status_code == 401

    finally:
        delete_user_by_email(email)


def test_retailer_cannot_delete_another_users_garment():
    """
    Verify that a retailer cannot delete another retailer's garment.
    """

    owner_email = "garment.api.delete.owner@example.com"
    other_email = "garment.api.delete.other@example.com"
    password = "SecurePassword123"

    delete_user_by_email(owner_email)
    delete_user_by_email(other_email)

    try:
        owner = create_test_user(
            email=owner_email,
            password=password,
            role="retailer",
        )

        other_user = create_test_user(
            email=other_email,
            password=password,
            role="retailer",
        )

        garment = create_garment_for_user(
            owner.user_id
        )

        headers = get_auth_headers(
            other_user
        )

        response = client.delete(
            f"/api/garments/{garment.garment_id}",
            headers=headers,
        )

        assert response.status_code == 404

        assert (
            response.json()["detail"]
            == "Garment not found."
        )

    finally:
        delete_user_by_email(owner_email)
        delete_user_by_email(other_email)