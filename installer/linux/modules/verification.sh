#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - Final Verification Module
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Final Installation Verification
# ------------------------------------------------------------

verify_installation() {

    log_section "SmartFit Installation Verification"

    verify_python
    verify_postgresql
    verify_backend
    verify_frontend

    log_success "All SmartFit installation checks passed."
}

# ------------------------------------------------------------
# Installation Summary
# ------------------------------------------------------------

print_installation_summary() {

    echo
    echo "============================================================"
    echo "SmartFit Installation Summary"
    echo "============================================================"

    echo
    echo "Project Root:"
    echo "  ${PROJECT_ROOT}"

    echo
    echo "Python:"
    echo "  $(\"${VENV_PYTHON}\" --version)"

    echo
    echo "Python Virtual Environment:"
    echo "  ${VENV_PATH}"

    echo
    echo "PostgreSQL:"
    echo "  PostgreSQL ${POSTGRESQL_MAJOR_VERSION}"

    echo
    echo "Main Database:"
    echo "  ${SMARTFIT_DATABASE}"

    echo
    echo "Test Database:"
    echo "  ${SMARTFIT_TEST_DATABASE}"

    echo
    echo "Backend:"
    echo "  ${BACKEND_ROOT}"

    echo
    echo "Backend Environment:"
    echo "  ${BACKEND_ENV_FILE}"

    echo
    echo "Pose Landmarker:"
    echo "  ${POSE_MODEL}"

    echo
    echo "Frontend:"
    echo "  ${FRONTEND_ROOT}"

    echo
    echo "Node.js:"
    echo "  $(node --version)"

    echo
    echo "npm:"
    echo "  $(npm --version)"

    echo
    echo "Production Build:"
    echo "  ${FRONTEND_ROOT}/dist"

    echo
    echo "============================================================"
}