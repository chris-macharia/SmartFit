"""
Tests for the SmartFit garment service.

This module verifies garment creation, retrieval, ownership
validation, updating, and deletion.
"""

import uuid

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.garment import Garment
from app.models.user import User
from app.services.garment_service import (
    create_garment,
    delete_garment,
    get_garment_by_id,
    get_garments_by_user,
    update_garment,
)


# ============================================================
# Test Helpers
# ============================================================


def create_test_user(
    email: str,
    password: str,
):
    """
    Create a test retailer.
    """

    db = SessionLocal()

    try:
        user = User(
            full_name="Garment Test Retailer",
            email=email,
            hashed_password=hash_password(password),
            role="retailer",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    finally:
        db.close()


def delete_test_user(email: str):
    """
    Delete a test user and all garments belonging to that user.
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

        # ----------------------------------------------------
        # Delete garments belonging to the test user.
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Delete the test user.
        # ----------------------------------------------------

        db.delete(user)
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# Garment Creation Tests
# ============================================================


def test_create_garment():
    """
    Verify that a retailer can create a garment and that
    the garment is persisted correctly.
    """

    email = "garment.service.create@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=52.5,
                waist_width=48.0,
                hip_width=54.5,
                shoulder_width=44.0,
                inseam=78.5,
            )

            # ------------------------------------------------
            # Verify garment was created.
            # ------------------------------------------------

            assert garment is not None
            assert garment.garment_id is not None

            # ------------------------------------------------
            # Verify ownership.
            # ------------------------------------------------

            assert garment.user_id == user.user_id

            # ------------------------------------------------
            # Verify measurements.
            # ------------------------------------------------

            assert float(garment.chest_width) == 52.5
            assert float(garment.waist_width) == 48.0
            assert float(garment.hip_width) == 54.5
            assert float(garment.shoulder_width) == 44.0
            assert float(garment.inseam) == 78.5

            # ------------------------------------------------
            # Verify timestamp.
            # ------------------------------------------------

            assert garment.created_at is not None

        finally:
            db.close()

    finally:
        delete_test_user(email)


# ============================================================
# Garment Retrieval Tests
# ============================================================


def test_get_garment_by_id():
    """
    Verify that a retailer can retrieve their own garment.
    """

    email = "garment.service.get@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            retrieved_garment = get_garment_by_id(
                db=db,
                garment_id=garment.garment_id,
                user_id=user.user_id,
            )

            assert retrieved_garment is not None
            assert (
                retrieved_garment.garment_id
                == garment.garment_id
            )
            assert (
                retrieved_garment.user_id
                == user.user_id
            )

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_get_garments_by_user():
    """
    Verify that all garments belonging to a retailer can be retrieved.
    """

    email = "garment.service.list@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        db = SessionLocal()

        try:
            first_garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            second_garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=54.0,
                waist_width=49.0,
                hip_width=56.0,
                shoulder_width=45.0,
                inseam=82.0,
            )

            garments = get_garments_by_user(
                db=db,
                user_id=user.user_id,
            )

            assert len(garments) == 2

            garment_ids = {
                garment.garment_id
                for garment in garments
            }

            assert first_garment.garment_id in garment_ids
            assert second_garment.garment_id in garment_ids

        finally:
            db.close()

    finally:
        delete_test_user(email)


# ============================================================
# Ownership Tests
# ============================================================


def test_user_cannot_retrieve_another_users_garment():
    """
    Verify that a retailer cannot retrieve another retailer's garment.
    """

    owner_email = "garment.service.owner@example.com"
    other_email = "garment.service.other@example.com"
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

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=owner.user_id,
                chest_width=52.0,
                waist_width=47.0,
                hip_width=54.0,
                shoulder_width=44.0,
                inseam=79.0,
            )

            retrieved_garment = get_garment_by_id(
                db=db,
                garment_id=garment.garment_id,
                user_id=other_user.user_id,
            )

            assert retrieved_garment is None

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)


# ============================================================
# Garment Update Tests
# ============================================================


def test_update_garment():
    """
    Verify that a retailer can update their own garment.
    """

    email = "garment.service.update@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            updated_garment = update_garment(
                db=db,
                garment_id=garment.garment_id,
                user_id=user.user_id,
                chest_width=55.0,
                waist_width=50.0,
            )

            assert updated_garment is not None

            assert float(
                updated_garment.chest_width
            ) == 55.0

            assert float(
                updated_garment.waist_width
            ) == 50.0

            # Fields not supplied to the update should
            # retain their original values.
            assert float(
                updated_garment.hip_width
            ) == 52.0

            assert float(
                updated_garment.shoulder_width
            ) == 43.0

            assert float(
                updated_garment.inseam
            ) == 80.0

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_user_cannot_update_another_users_garment():
    """
    Verify that a retailer cannot update another retailer's garment.
    """

    owner_email = "garment.service.update.owner@example.com"
    other_email = "garment.service.update.other@example.com"
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

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=owner.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            updated_garment = update_garment(
                db=db,
                garment_id=garment.garment_id,
                user_id=other_user.user_id,
                chest_width=60.0,
            )

            assert updated_garment is None

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)


# ============================================================
# Garment Deletion Tests
# ============================================================


def test_delete_garment():
    """
    Verify that a retailer can delete their own garment.
    """

    email = "garment.service.delete@example.com"
    password = "SecurePassword123"

    delete_test_user(email)

    try:
        user = create_test_user(
            email=email,
            password=password,
        )

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=user.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            deleted = delete_garment(
                db=db,
                garment_id=garment.garment_id,
                user_id=user.user_id,
            )

            assert deleted is True

            retrieved_garment = get_garment_by_id(
                db=db,
                garment_id=garment.garment_id,
                user_id=user.user_id,
            )

            assert retrieved_garment is None

        finally:
            db.close()

    finally:
        delete_test_user(email)


def test_user_cannot_delete_another_users_garment():
    """
    Verify that a retailer cannot delete another retailer's garment.
    """

    owner_email = "garment.service.delete.owner@example.com"
    other_email = "garment.service.delete.other@example.com"
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

        db = SessionLocal()

        try:
            garment = create_garment(
                db=db,
                user_id=owner.user_id,
                chest_width=50.0,
                waist_width=45.0,
                hip_width=52.0,
                shoulder_width=43.0,
                inseam=80.0,
            )

            deleted = delete_garment(
                db=db,
                garment_id=garment.garment_id,
                user_id=other_user.user_id,
            )

            assert deleted is False

            # Confirm that the original owner still has
            # access to the garment.
            retrieved_garment = get_garment_by_id(
                db=db,
                garment_id=garment.garment_id,
                user_id=owner.user_id,
            )

            assert retrieved_garment is not None

        finally:
            db.close()

    finally:
        delete_test_user(owner_email)
        delete_test_user(other_email)