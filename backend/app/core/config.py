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
            to the SmartFit PostgreSQL database.
    """

    # Retrieve the database connection URL from the environment.
    #
    # If DATABASE_URL is not defined, an empty string is returned.
    # The database connection layer will later detect an invalid or
    # missing URL when it attempts to create the database engine.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")


# Create a single Settings instance that can be imported and reused
# throughout the application.
#
# Other modules can access the database URL using:
#
#     from app.core.config import settings
#     settings.DATABASE_URL
#
settings = Settings()