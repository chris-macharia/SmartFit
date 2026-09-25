#!/usr/bin/env bash

# ============================================================
# SmartFit v0.0.1
# Installer Logging and Utility Functions
# ============================================================
#
# Shared logging, command execution, environment, and
# failure-handling functions.
#
# IMPORTANT:
#   This file does NOT determine PROJECT_ROOT.
#   setup.sh is responsible for determining and exporting it.
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

log_info() {
    echo "[INFO] $*"
}

log_success() {
    echo "[SUCCESS] $*"
}

log_warning() {
    echo "[WARNING] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_section() {
    echo
    echo "============================================================"
    echo "$*"
    echo "============================================================"
}

# ------------------------------------------------------------
# Failure
# ------------------------------------------------------------

fail() {
    log_error "$*"
    exit 1
}

# ------------------------------------------------------------
# Command Check
# ------------------------------------------------------------

require_command() {

    local command_name="$1"

    if command -v "${command_name}" >/dev/null 2>&1; then
        log_success "Found command: ${command_name}"
    else
        fail "Required command not found: ${command_name}"
    fi
}

# ------------------------------------------------------------
# Directory Check
# ------------------------------------------------------------

require_directory() {

    local directory="$1"

    if [[ ! -d "${directory}" ]]; then
        fail "Required directory not found: ${directory}"
    fi
}

# ------------------------------------------------------------
# File Check
# ------------------------------------------------------------

require_file() {

    local file_path="$1"

    if [[ ! -f "${file_path}" ]]; then
        fail "Required file not found: ${file_path}"
    fi
}

# ------------------------------------------------------------
# Linux Check
# ------------------------------------------------------------

require_linux() {

    if [[ "$(uname -s)" != "Linux" ]]; then
        fail "This installer is intended for Linux."
    fi

    if [[ -f /etc/os-release ]]; then
        # shellcheck disable=SC1091
        source /etc/os-release

        log_info "Operating system: ${PRETTY_NAME:-Unknown}"
    fi
}

# ------------------------------------------------------------
# UTF-8 / BOM-Safe File Replacement
# ------------------------------------------------------------

write_utf8_no_bom() {

    local destination="$1"
    local content="$2"

    printf '%s' "${content}" > "${destination}"

    # Remove UTF-8 BOM if one somehow exists.
    if [[ -f "${destination}" ]]; then
        if LC_ALL=C grep -q $'^\xEF\xBB\xBF' "${destination}" 2>/dev/null; then
            tail -c +4 "${destination}" > "${destination}.tmp"
            mv "${destination}.tmp" "${destination}"
        fi
    fi
}

# ------------------------------------------------------------
# URL Password Encoding
# ------------------------------------------------------------

url_encode() {

    local value="$1"

    python3 - "${value}" <<'PY'
import sys
from urllib.parse import quote

value = sys.argv[1]
print(quote(value, safe=""))
PY
}

# ------------------------------------------------------------
# URL Password Extraction
# ------------------------------------------------------------

extract_url_password() {

    local url="$1"

    python3 - "${url}" <<'PY'
import sys
from urllib.parse import urlsplit

url = sys.argv[1]
parsed = urlsplit(url)

if parsed.password is None:
    sys.exit(0)

print(parsed.password)
PY
}