#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - Backend Module
# ============================================================
#
# Responsibilities:
#   - Verify backend structure
#   - Verify bundled Pose Landmarker model
#   - Reset backend databases
#   - Run complete pytest suite
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

BACKEND_ROOT="${PROJECT_ROOT}/backend"
VENV_PYTHON="${BACKEND_ROOT}/.venv/bin/python"

POSE_MODEL="${BACKEND_ROOT}/models/pose_landmarker_lite.task"

RESET_SCRIPT="${BACKEND_ROOT}/scripts/reset_databases.py"

export BACKEND_ROOT
export VENV_PYTHON
export POSE_MODEL
export RESET_SCRIPT

# ------------------------------------------------------------
# Backend Structure
# ------------------------------------------------------------

verify_backend_structure() {

    require_directory "${BACKEND_ROOT}"

    require_file "${BACKEND_ROOT}/app/main.py"
    require_file "${BACKEND_ROOT}/requirements.txt"
    require_file "${BACKEND_ROOT}/.env"

    require_directory "${BACKEND_ROOT}/app"
    require_directory "${BACKEND_ROOT}/models"
    require_directory "${BACKEND_ROOT}/scripts"
    require_directory "${BACKEND_ROOT}/tests"

    log_success "SmartFit backend structure verified."
}

# ------------------------------------------------------------
# Pose Landmarker Model
# ------------------------------------------------------------

verify_pose_model() {

    require_file "${POSE_MODEL}"

    local model_size

    model_size="$(stat -c '%s' "${POSE_MODEL}")"

    if [[ "${model_size}" -le 0 ]]; then
        fail "Pose Landmarker model is empty."
    fi

    log_success "Bundled pose_landmarker_lite.task verified."
    log_info "Model size: ${model_size} bytes"
}

# ------------------------------------------------------------
# Database Reset
# ------------------------------------------------------------

reset_backend_databases() {

    require_file "${RESET_SCRIPT}"
    require_file "${VENV_PYTHON}"

    log_info "Resetting SmartFit backend databases..."

    cd "${BACKEND_ROOT}"

    "${VENV_PYTHON}" \
        -m scripts.reset_databases \
        --target both

    log_success "SmartFit databases reset successfully."
}

# ------------------------------------------------------------
# Complete Pytest Suite
# ------------------------------------------------------------

run_backend_tests() {

    require_file "${VENV_PYTHON}"

    cd "${BACKEND_ROOT}"

    log_info "Running complete SmartFit backend pytest suite..."

    "${VENV_PYTHON}" -m pytest

    log_success "Complete SmartFit backend pytest suite passed."
}

# ------------------------------------------------------------
# Backend Verification
# ------------------------------------------------------------

verify_backend() {

    require_file "${BACKEND_ROOT}/app/main.py"
    require_file "${BACKEND_ROOT}/.env"
    require_file "${VENV_PYTHON}"
    require_file "${POSE_MODEL}"

    log_success "Backend installation verified."
}