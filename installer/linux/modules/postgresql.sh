#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - PostgreSQL Module
# ============================================================
#
# Requirements:
#   - PostgreSQL 18
#   - SmartFit_db
#   - SmartFit_Test_db
#   - Preserve existing PostgreSQL password
#   - Preserve unrelated backend/.env configuration
#   - Synchronize DATABASE_URL
#   - Synchronize TEST_DATABASE_URL
#   - UTF-8 without BOM
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

POSTGRESQL_MAJOR_VERSION="18"

SMARTFIT_DATABASE="SmartFit_db"
SMARTFIT_TEST_DATABASE="SmartFit_Test_db"

BACKEND_ROOT="${PROJECT_ROOT}/backend"
BACKEND_ENV_FILE="${BACKEND_ROOT}/.env"

POSTGRES_USER="postgres"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

export POSTGRESQL_MAJOR_VERSION
export SMARTFIT_DATABASE
export SMARTFIT_TEST_DATABASE
export BACKEND_ENV_FILE

# ------------------------------------------------------------
# PostgreSQL Version
# ------------------------------------------------------------

get_postgresql_version() {

    if ! command -v psql >/dev/null 2>&1; then
        return 1
    fi

    psql --version |
        sed -E 's/.* ([0-9]+)\..*/\1/'
}

# ------------------------------------------------------------
# Install PostgreSQL 18
# ------------------------------------------------------------

install_postgresql() {

    local installed_version=""

    if installed_version="$(get_postgresql_version 2>/dev/null)"; then

        if [[ "${installed_version}" == "${POSTGRESQL_MAJOR_VERSION}" ]]; then
            log_success "PostgreSQL ${POSTGRESQL_MAJOR_VERSION} is already installed."
        else
            fail "PostgreSQL ${installed_version} is installed, but SmartFit requires PostgreSQL ${POSTGRESQL_MAJOR_VERSION}."
        fi

    else

        log_info "Installing PostgreSQL ${POSTGRESQL_MAJOR_VERSION}..."

        sudo apt-get update

        # PostgreSQL 18 is obtained from the PostgreSQL APT repository.
        sudo apt-get install -y \
            curl \
            ca-certificates \
            gnupg

        if [[ ! -f /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc ]]; then

            sudo install -d /usr/share/postgresql-common/pgdg

            sudo curl -fsSLo \
                /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
                https://www.postgresql.org/media/keys/ACCC4CF8.asc
        fi

        local codename

        codename="$(
            . /etc/os-release
            echo "${VERSION_CODENAME}"
        )"

        echo \
            "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] http://apt.postgresql.org/pub/repos/apt ${codename}-pgdg main" |
            sudo tee /etc/apt/sources.list.d/pgdg.list >/dev/null

        sudo apt-get update

        sudo apt-get install -y \
            "postgresql-${POSTGRESQL_MAJOR_VERSION}" \
            "postgresql-client-${POSTGRESQL_MAJOR_VERSION}"

        log_success "PostgreSQL ${POSTGRESQL_MAJOR_VERSION} installed."
    fi

    sudo systemctl enable postgresql
    sudo systemctl start postgresql
}

# ------------------------------------------------------------
# Configure PostgreSQL
# ------------------------------------------------------------

configure_postgresql() {

    if sudo -u postgres pg_isready >/dev/null 2>&1; then
        log_success "PostgreSQL server is ready."
    else
        log_info "Starting PostgreSQL..."

        sudo systemctl start postgresql

        if ! sudo -u postgres pg_isready >/dev/null 2>&1; then
            fail "PostgreSQL server is not ready."
        fi
    fi
}

# ------------------------------------------------------------
# Database Existence
# ------------------------------------------------------------

database_exists() {

    local database_name="$1"

    sudo -u postgres psql \
        -tAc "SELECT 1 FROM pg_database WHERE datname='${database_name}'" |
        grep -q '^1$'
}

# ------------------------------------------------------------
# Create Database
# ------------------------------------------------------------

create_database_if_missing() {

    local database_name="$1"

    if database_exists "${database_name}"; then
        log_success "Database already exists: ${database_name}"
        return 0
    fi

    log_info "Creating database: ${database_name}"

    sudo -u postgres createdb "${database_name}"

    log_success "Database created: ${database_name}"
}

# ------------------------------------------------------------
# Existing .env Password
# ------------------------------------------------------------

get_existing_database_password() {

    if [[ ! -f "${BACKEND_ENV_FILE}" ]]; then
        return 1
    fi

    local database_url

    database_url="$(
        grep '^DATABASE_URL=' "${BACKEND_ENV_FILE}" |
        head -n 1 |
        cut -d '=' -f 2-
    )"

    if [[ -z "${database_url}" ]]; then
        return 1
    fi

    extract_url_password "${database_url}"
}

# ------------------------------------------------------------
# Existing PostgreSQL Password
# ------------------------------------------------------------

resolve_postgres_password() {

    local existing_password=""

    if existing_password="$(get_existing_database_password 2>/dev/null)"; then

        if [[ -n "${existing_password}" ]]; then
            POSTGRES_PASSWORD="${existing_password}"
            export POSTGRES_PASSWORD

            log_success "Existing PostgreSQL password preserved from backend/.env."
            return 0
        fi
    fi

    # Do not overwrite an existing password when the .env does not
    # expose one. Local PostgreSQL administration through the
    # postgres OS account remains available.
    POSTGRES_PASSWORD=""

    export POSTGRES_PASSWORD

    log_info "No PostgreSQL password was found in backend/.env."
}

# ------------------------------------------------------------
# URL Construction
# ------------------------------------------------------------

build_database_url() {

    local database_name="$1"

    if [[ -n "${POSTGRES_PASSWORD}" ]]; then

        local encoded_password

        encoded_password="$(url_encode "${POSTGRES_PASSWORD}")"

        echo \
            "postgresql://${POSTGRES_USER}:${encoded_password}@${POSTGRES_HOST}:${POSTGRES_PORT}/${database_name}"

    else

        echo \
            "postgresql://${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${database_name}"
    fi
}

# ------------------------------------------------------------
# Preserve .env and Synchronize Database URLs
# ------------------------------------------------------------

update_backend_environment() {

    require_directory "${BACKEND_ROOT}"

    local database_url
    local test_database_url

    database_url="$(build_database_url "${SMARTFIT_DATABASE}")"
    test_database_url="$(build_database_url "${SMARTFIT_TEST_DATABASE}")"

    local temp_file

    temp_file="$(mktemp)"

    # Preserve the existing .env when present.
    if [[ -f "${BACKEND_ENV_FILE}" ]]; then
        cp "${BACKEND_ENV_FILE}" "${temp_file}"
    else
        : > "${temp_file}"
    fi

    # Remove only the two managed database URL variables.
    sed -i \
        '/^[[:space:]]*DATABASE_URL[[:space:]]*=/d' \
        "${temp_file}"

    sed -i \
        '/^[[:space:]]*TEST_DATABASE_URL[[:space:]]*=/d' \
        "${temp_file}"

    {
        echo "DATABASE_URL=${database_url}"
        echo "TEST_DATABASE_URL=${test_database_url}"
    } >> "${temp_file}"

    # Write as UTF-8 without BOM.
    python3 - "${temp_file}" "${BACKEND_ENV_FILE}" <<'PY'
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])

text = source.read_text(encoding="utf-8-sig")

# Explicitly remove BOM if present.
text = text.lstrip("\ufeff")

destination.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)
PY

    rm -f "${temp_file}"

    log_success "backend/.env preserved and database URLs synchronized."
}

# ------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------

configure_smartfit_database() {

    resolve_postgres_password

    create_database_if_missing "${SMARTFIT_DATABASE}"
    create_database_if_missing "${SMARTFIT_TEST_DATABASE}"

    log_success "SmartFit databases verified."
}

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

verify_postgresql() {

    require_command psql

    local version

    version="$(get_postgresql_version)"

    if [[ "${version}" != "${POSTGRESQL_MAJOR_VERSION}" ]]; then
        fail "Expected PostgreSQL ${POSTGRESQL_MAJOR_VERSION}, found PostgreSQL ${version}."
    fi

    if ! sudo -u postgres pg_isready >/dev/null 2>&1; then
        fail "PostgreSQL server is not ready."
    fi

    if ! database_exists "${SMARTFIT_DATABASE}"; then
        fail "Database ${SMARTFIT_DATABASE} does not exist."
    fi

    if ! database_exists "${SMARTFIT_TEST_DATABASE}"; then
        fail "Database ${SMARTFIT_TEST_DATABASE} does not exist."
    fi

    require_file "${BACKEND_ENV_FILE}"

    if ! grep -q '^DATABASE_URL=' "${BACKEND_ENV_FILE}"; then
        fail "DATABASE_URL is missing from backend/.env."
    fi

    if ! grep -q '^TEST_DATABASE_URL=' "${BACKEND_ENV_FILE}"; then
        fail "TEST_DATABASE_URL is missing from backend/.env."
    fi

    log_success "PostgreSQL ${version} verified."
    log_success "${SMARTFIT_DATABASE} verified."
    log_success "${SMARTFIT_TEST_DATABASE} verified."
}