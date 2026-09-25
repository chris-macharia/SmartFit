#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - Main Entry Point
# ============================================================
#
# This script coordinates the complete SmartFit installation.
#
# Responsibilities:
#   - Determine the SmartFit project root
#   - Load installer modules
#   - Install/configure Python 3.12.x
#   - Create backend/.venv
#   - Install/configure PostgreSQL 18
#   - Preserve/update backend/.env
#   - Synchronize DATABASE_URL and TEST_DATABASE_URL
#   - Verify the bundled MediaPipe model
#   - Reset SmartFit databases
#   - Run the complete backend pytest suite
#   - Install/reuse Node.js LTS and npm dependencies
#   - Build the React/Vite frontend
#   - Perform final installation verification
#
# IMPORTANT:
#   This file determines PROJECT_ROOT.
#   Individual modules must not independently redefine it.
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Determine Project Root
# ------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PROJECT_ROOT

# ------------------------------------------------------------
# Installer Paths
# ------------------------------------------------------------

INSTALLER_ROOT="${PROJECT_ROOT}/installer/linux"
MODULES_ROOT="${INSTALLER_ROOT}/modules"

export INSTALLER_ROOT
export MODULES_ROOT

# ------------------------------------------------------------
# Load Modules
# ------------------------------------------------------------

source "${MODULES_ROOT}/logging.sh"
source "${MODULES_ROOT}/python.sh"
source "${MODULES_ROOT}/postgresql.sh"
source "${MODULES_ROOT}/backend.sh"
source "${MODULES_ROOT}/frontend.sh"
source "${MODULES_ROOT}/verification.sh"

# ------------------------------------------------------------
# Main Installation
# ------------------------------------------------------------

main() {

    log_section "SmartFit v0.0.1 - Linux Installer"

    log_info "Project root: ${PROJECT_ROOT}"

    # --------------------------------------------------------
    # Basic Environment
    # --------------------------------------------------------

    require_linux

    require_directory "${PROJECT_ROOT}"

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    log_section "Python 3.12.x Environment"

    install_python
    create_python_environment
    install_python_dependencies

    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------

    log_section "PostgreSQL 18"

    install_postgresql
    configure_postgresql
    configure_smartfit_database
    update_backend_environment

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    log_section "SmartFit Backend"

    verify_backend_structure
    verify_pose_model
    reset_backend_databases
    run_backend_tests

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    log_section "SmartFit Frontend"

    install_node_lts
    validate_npm_dependencies
    install_frontend_dependencies
    build_frontend

    # --------------------------------------------------------
    # Final Verification
    # --------------------------------------------------------

    log_section "Final Installation Verification"

    verify_python
    verify_postgresql
    verify_backend
    verify_frontend

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print_installation_summary

    log_success "SmartFit installation completed successfully."
}

# ------------------------------------------------------------
# Execute
# ------------------------------------------------------------

main "$@"