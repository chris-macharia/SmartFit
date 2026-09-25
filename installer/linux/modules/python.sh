#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - Python Environment Module
# ============================================================
#
# Requirements:
#   - Python 3.12.x
#   - backend/.venv
#   - backend/requirements.txt
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

BACKEND_ROOT="${PROJECT_ROOT}/backend"
VENV_PATH="${BACKEND_ROOT}/.venv"
VENV_PYTHON="${VENV_PATH}/bin/python"
REQUIREMENTS_FILE="${BACKEND_ROOT}/requirements.txt"

export BACKEND_ROOT
export VENV_PATH
export VENV_PYTHON
export REQUIREMENTS_FILE

# ------------------------------------------------------------
# Find Python 3.12
# ------------------------------------------------------------

find_python_312() {

    local candidates=(
        "python3.12"
        "python3"
    )

    local candidate
    local version

    for candidate in "${candidates[@]}"; do

        if ! command -v "${candidate}" >/dev/null 2>&1; then
            continue
        fi

        version="$("${candidate}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"

        if [[ "${version}" == "3.12" ]]; then
            echo "${candidate}"
            return 0
        fi
    done

    return 1
}

# ------------------------------------------------------------
# Install Python 3.12
# ------------------------------------------------------------

install_python() {

    local python_command

    if python_command="$(find_python_312)"; then

        PYTHON_COMMAND="${python_command}"
        export PYTHON_COMMAND

        log_success "Python 3.12.x found: ${PYTHON_COMMAND}"

        return 0
    fi

    log_info "Python 3.12.x was not found."

    sudo apt-get update

    sudo apt-get install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev

    if ! python_command="$(find_python_312)"; then
        fail "Python 3.12.x could not be installed."
    fi

    PYTHON_COMMAND="${python_command}"
    export PYTHON_COMMAND

    log_success "Python 3.12.x installed."
}

# ------------------------------------------------------------
# Create Virtual Environment
# ------------------------------------------------------------

create_python_environment() {

    require_directory "${BACKEND_ROOT}"

    if [[ -x "${VENV_PYTHON}" ]]; then

        local venv_version

        venv_version="$(
            "${VENV_PYTHON}" -c \
            'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
        )"

        if [[ "${venv_version}" == "3.12" ]]; then
            log_success "Existing backend/.venv uses Python 3.12.x."
            return 0
        fi

        log_warning "Existing backend/.venv does not use Python 3.12."
        log_info "Recreating backend/.venv."

        rm -rf "${VENV_PATH}"
    fi

    log_info "Creating backend/.venv with Python 3.12.x..."

    "${PYTHON_COMMAND}" -m venv "${VENV_PATH}"

    require_file "${VENV_PYTHON}"

    log_success "backend/.venv created."
}

# ------------------------------------------------------------
# Install Backend Dependencies
# ------------------------------------------------------------

install_python_dependencies() {

    require_file "${REQUIREMENTS_FILE}"

    log_info "Updating pip..."

    "${VENV_PYTHON}" -m pip install --upgrade pip

    log_info "Installing SmartFit backend dependencies..."

    "${VENV_PYTHON}" -m pip install \
        -r "${REQUIREMENTS_FILE}"

    log_success "Backend Python dependencies installed."
}

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

verify_python() {

    require_file "${VENV_PYTHON}"

    local version

    version="$(
        "${VENV_PYTHON}" -c \
        'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")'
    )"

    if [[ "${version}" != 3.12.* ]]; then
        fail "SmartFit requires Python 3.12.x, but backend/.venv uses ${version}."
    fi

    log_success "Python version: ${version}"
    log_success "Virtual environment: ${VENV_PATH}"
}