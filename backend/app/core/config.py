"""
Application configuration module for SmartFit.

This module is responsible for loading environment variables from the
.env file and making application-wide configuration settings available
to the rest of the SmartFit backend.

Keeping configuration in one place makes the application easier to
maintain and prevents environment-specific values, such as database
credentials and JWT secrets, from being hard-coded throughout the
codebase.
"""

import os

from dotenv import load_dotenv


# Load environment variables from the .env file.
#
# This allows the application to access configuration values without
# hard-coding sensitive information directly into the Python source code.
load_dotenv()


class Settings:
    """
    Stores application-wide configuration settings.

    Attributes:
        DATABASE_URL:
            Connection URL used by SQLAlchemy to connect to the
            SmartFit development PostgreSQL database.

        TEST_DATABASE_URL:
            Connection URL used by automated tests.

        SECRET_KEY:
            Secret key used to sign JWT access tokens.

        ALGORITHM:
            Cryptographic algorithm used to sign JWT access tokens.

        ACCESS_TOKEN_EXPIRE_MINUTES:
            Number of minutes before a JWT access token expires.
    """

    # ============================================================
    # Database Configuration
    # ============================================================

    # Retrieve the development database connection URL.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Retrieve the dedicated test database connection URL.
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "")


    # ============================================================
    # JWT Authentication Configuration
    # ============================================================

    # Retrieve the secret key used to sign JWT access tokens.
    #
    # This value must be kept private and should never be committed
    # to the Git repository.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    # Retrieve the JWT signing algorithm.
    #
    # HS256 is a commonly used symmetric signing algorithm.
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Retrieve the number of minutes before an access token expires.
    #
    # The environment variable is stored as text, so it is converted
    # to an integer before being used by the application.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )


# Create a single Settings instance that can be imported and reused
# throughout the application.
#
# Other modules can access configuration values using:
#
#     from app.core.config import settings
#
#     settings.DATABASE_URL
#     settings.SECRET_KEY
#     settings.ALGORITHM
#
settings = Settings()