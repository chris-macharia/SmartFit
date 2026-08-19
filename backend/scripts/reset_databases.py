"""
Reset SmartFit local development and test databases.

This script is intended only for disposable local databases. It removes
every table and all data in the PostgreSQL public schema, then recreates
the current SmartFit schema from the SQLAlchemy models.

Examples:
    python -m scripts.reset_databases --target development
    python -m scripts.reset_databases --target test
    python -m scripts.reset_databases --target both
"""

import argparse

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.db.database import Base

# Import every model before create_all() so SQLAlchemy knows about all
# current SmartFit tables, including the Milestone 5 columns.
from app.models import (
    Avatar,
    BodyMeasurement,
    Garment,
    User,
    Video,
    VirtualFitting,
)


# The imports above register models with Base.metadata. Assigning them to a
# private tuple makes that purpose explicit while avoiding unused-import
# confusion for readers and static-analysis tools.
_REGISTERED_MODELS = (
    Avatar,
    BodyMeasurement,
    Garment,
    User,
    Video,
    VirtualFitting,
)


DATABASE_TARGETS = {
    "development": settings.DATABASE_URL,
    "test": settings.TEST_DATABASE_URL,
}


def _parse_arguments() -> argparse.Namespace:
    """Read the database target selected by the developer."""

    parser = argparse.ArgumentParser(
        description=(
            "Delete all SmartFit tables in a local database and recreate "
            "the current schema."
        )
    )
    parser.add_argument(
        "--target",
        choices=("development", "test", "both"),
        default="development",
        help=(
            "Database to reset. Defaults to development; use both to reset "
            "development and test databases."
        ),
    )

    return parser.parse_args()


def _targets_to_reset(target: str) -> list[tuple[str, str]]:
    """Return configured connection URLs for the requested reset target."""

    target_names = (
        ("development", "test")
        if target == "both"
        else (target,)
    )
    targets: list[tuple[str, str]] = []

    for target_name in target_names:
        database_url = DATABASE_TARGETS[target_name]

        if not database_url:
            raise ValueError(
                f"{target_name.title()} database URL is not configured."
            )

        targets.append((target_name, database_url))

    return targets


def _confirm_reset(targets: list[tuple[str, str]]) -> None:
    """Require an explicit acknowledgement before deleting any data."""

    print("WARNING: This permanently deletes all SmartFit database tables and data.")
    print("The following local database target(s) will be reset:")

    for target_name, database_url in targets:
        safe_url = create_engine(database_url).url.render_as_string(
            hide_password=True
        )
        print(f"- {target_name}: {safe_url}")

    confirmation = input(
        "Type RESET SMARTFIT DATABASES to continue: "
    )

    if confirmation != "RESET SMARTFIT DATABASES":
        raise SystemExit("Database reset cancelled. No changes were made.")


def _reset_database(target_name: str, database_url: str) -> None:
    """Drop the public schema for one database and recreate SmartFit tables."""

    engine = create_engine(database_url)

    try:
        # DDL is executed in one transaction. CASCADE removes all tables,
        # foreign keys, indexes, and data belonging to the public schema.
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))

        # Rebuild the complete schema from the current model definitions.
        # This creates a clean Milestone 5 database without needing a
        # migration from an earlier schema.
        Base.metadata.create_all(bind=engine)

        print(f"{target_name.title()} database reset successfully.")

    finally:
        # Release database connections so the script exits cleanly.
        engine.dispose()


def main() -> None:
    """Run the guarded SmartFit database reset workflow."""

    arguments = _parse_arguments()
    targets = _targets_to_reset(arguments.target)
    _confirm_reset(targets)

    for target_name, database_url in targets:
        _reset_database(target_name, database_url)


if __name__ == "__main__":
    main()
