"""
Tests for SmartFit password hashing utilities.

These tests verify that:

1. Passwords are converted into hashes.
2. Password hashes are not identical to plain-text passwords.
3. The original password can be successfully verified.
4. An incorrect password fails verification.
5. Hashing the same password twice produces different hashes.
"""

from app.core.security import hash_password, verify_password


def test_password_is_hashed():
    """
    Verify that a plain-text password is converted into a hash.
    """

    password = "SecurePassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_correct_password_is_verified():
    """
    Verify that the original password successfully matches
    its generated password hash.
    """

    password = "SecurePassword123"

    hashed_password = hash_password(password)

    assert verify_password(
        password,
        hashed_password
    ) is True


def test_incorrect_password_is_rejected():
    """
    Verify that an incorrect password does not match
    the stored password hash.
    """

    password = "SecurePassword123"
    incorrect_password = "WrongPassword123"

    hashed_password = hash_password(password)

    assert verify_password(
        incorrect_password,
        hashed_password
    ) is False


def test_same_password_generates_different_hashes():
    """
    Verify that hashing the same password twice produces
    different hashes due to bcrypt's random salt.

    This is an important security property of password hashing.
    """

    password = "SecurePassword123"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_generated_hash_can_be_verified():
    """
    Verify that a generated password hash can be used
    to authenticate the original password.
    """

    password = "AnotherSecurePassword456"

    hashed_password = hash_password(password)

    assert verify_password(
        password,
        hashed_password
    ) is True