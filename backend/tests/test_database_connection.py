"""
Database connection tests for SmartFit.

This module contains automated tests used to verify that the
SmartFit backend can successfully communicate with the
PostgreSQL database configured for the application.

The tests use SQLAlchemy to establish a database connection
and execute a simple, non-destructive SQL query.
"""

from sqlalchemy import text

from app.db.database import engine


def test_database_connection():
    """
    Verify that the SmartFit backend can connect to PostgreSQL.

    The test opens a connection using the SQLAlchemy engine
    configured in the application's database module. It then
    executes the SQL statement `SELECT 1`.

    `SELECT 1` is used because it does not modify or delete
    any data. A successful execution confirms that:

    1. The PostgreSQL server is running.
    2. The database credentials are valid.
    3. The configured database exists and is accessible.
    4. SQLAlchemy can establish a connection.
    5. The backend can communicate with PostgreSQL.
    """

    # Open a connection to the PostgreSQL database using
    # the SQLAlchemy engine configured for SmartFit.
    with engine.connect() as connection:

        # Execute a simple, non-destructive SQL statement.
        #
        # SELECT 1 does not modify the database. It is simply
        # used to verify that the connection is working correctly.
        result = connection.execute(text("SELECT 1"))

        # Retrieve the first value returned by the query.
        # The expected result is the integer 1.
        value = result.scalar()

        # Confirm that PostgreSQL returned the expected value.
        # If the value is not 1, the test will fail.
        assert value == 1