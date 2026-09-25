#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Linux Installer - Frontend Module
# ============================================================
#
# Responsibilities:
#   - Install Node.js LTS
#   - Reuse existing npm dependencies when possible
#   - Validate dependencies with npm ci --dry-run
#   - Run npm ci / npm install as appropriate
#   - Build React/Vite production bundle
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

FRONTEND_ROOT="${PROJECT_ROOT}/frontend"
NODE_MODULES="${FRONTEND_ROOT}/node_modules"
PACKAGE_JSON="${FRONTEND_ROOT}/package.json"
PACKAGE_LOCK="${FRONTEND_ROOT}/package-lock.json"

export FRONTEND_ROOT
export NODE_MODULES
export PACKAGE_JSON
export PACKAGE_LOCK

# ------------------------------------------------------------
# Node.js LTS
# ------------------------------------------------------------

install_node_lts() {

    if command -v node >/dev/null 2>&1; then

        local node_version

        node_version="$(node --version)"

        log_success "Node.js already installed: ${node_version}"

    else

        log_info "Node.js is not installed."

        # NodeSource's LTS channel is used so the installer does not
        # hard-code an obsolete LTS major version.
        sudo apt-get update

        sudo apt-get install -y \
            curl \
            ca-certificates

        curl -fsSL https://deb.nodesource.com/setup_lts.x |
            sudo -E bash -

        sudo apt-get install -y nodejs

        log_success "Node.js LTS installed."
    fi

    require_command node
    require_command npm

    log_info "Node.js version: $(node --version)"
    log_info "npm version: $(npm --version)"
}

# ------------------------------------------------------------
# Package Metadata
# ------------------------------------------------------------

verify_frontend_package() {

    require_directory "${FRONTEND_ROOT}"
    require_file "${PACKAGE_JSON}"

    if [[ ! -f "${PACKAGE_LOCK}" ]]; then
        log_warning "package-lock.json was not found."
        log_warning "npm install will be used instead of npm ci."
    fi
}

# ------------------------------------------------------------
# npm ci Dry Run
# ------------------------------------------------------------

validate_npm_dependencies() {

    verify_frontend_package

    cd "${FRONTEND_ROOT}"

    if [[ ! -f "${PACKAGE_LOCK}" ]]; then
        log_info "Skipping npm ci --dry-run because package-lock.json is absent."
        return 0
    fi

    log_info "Validating npm dependencies with npm ci --dry-run..."

    npm ci --dry-run

    log_success "npm dependency validation passed."
}

# ------------------------------------------------------------
# Install / Reuse npm Dependencies
# ------------------------------------------------------------

install_frontend_dependencies() {

    verify_frontend_package

    cd "${FRONTEND_ROOT}"

    # --------------------------------------------------------
    # Existing node_modules
    # --------------------------------------------------------

    if [[ -d "${NODE_MODULES}" ]]; then

        log_info "Existing node_modules directory found."

        if [[ -f "${PACKAGE_LOCK}" ]]; then

            log_info "Validating existing dependencies against package-lock.json..."

            if npm ci --dry-run >/dev/null 2>&1; then
                log_success "Existing npm dependencies are reusable."

                # Do not unnecessarily delete/reinstall a valid
                # dependency tree.
                return 0
            fi

            log_warning "Existing node_modules does not match package-lock.json."
            log_info "Reinstalling dependencies with npm ci."

            npm ci

            log_success "npm ci completed."
            return 0

        else

            log_success "Existing node_modules will be reused."
            return 0
        fi
    fi

    # --------------------------------------------------------
    # Fresh installation
    # --------------------------------------------------------

    if [[ -f "${PACKAGE_LOCK}" ]]; then

        log_info "Installing dependencies using npm ci..."

        npm ci

        log_success "npm ci completed."

    else

        log_info "Installing dependencies using npm install..."

        npm install

        log_success "npm install completed."
    fi
}

# ------------------------------------------------------------
# React/Vite Production Build
# ------------------------------------------------------------

build_frontend() {

    verify_frontend_package

    cd "${FRONTEND_ROOT}"

    log_info "Building SmartFit React/Vite production bundle..."

    npm run build

    if [[ ! -d "${FRONTEND_ROOT}/dist" ]]; then
        fail "React/Vite production build did not create the dist directory."
    fi

    log_success "React/Vite production build completed."
}

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

verify_frontend() {

    require_file "${PACKAGE_JSON}"

    if [[ ! -d "${NODE_MODULES}" ]]; then
        fail "frontend/node_modules was not found."
    fi

    if [[ ! -d "${FRONTEND_ROOT}/dist" ]]; then
        fail "Frontend production build directory was not found."
    fi

    log_success "Frontend installation verified."
}