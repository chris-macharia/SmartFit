"""
Application configuration module for SmartFit.

This module is responsible for loading environment variables from the
.env file and making application-wide configuration settings available
to the rest of the SmartFit backend.

Keeping configuration in one place makes the application easier to
maintain and prevents environment-specific values, such as database
credentials, from being hard-coded throughout the codebase.
"""

import os

from dotenv import load_dotenv


# Load environment variables from the .env file.
#
# This allows the application to access configuration values such as
# DATABASE_URL without hard-coding sensitive information directly
# into the Python source code.
load_dotenv()


class Settings:
    """
    Stores application-wide configuration settings.

    Attributes:
        DATABASE_URL: Connection URL used by SQLAlchemy to connect
            to the SmartFit development PostgreSQL database.

        TEST_DATABASE_URL: Connection URL used by the automated
            pytest suite to connect to the isolated test database.
    """

    # Development database connection.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Test database connection.
    #
    # This database is used exclusively by automated tests.
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "")


# Create a single Settings instance that can be imported and reused
# throughout the application.
#
# Other modules can access the database URL using:
#
#     from app.core.config import settings
#     settings.DATABASE_URL
#
settings = Settings()