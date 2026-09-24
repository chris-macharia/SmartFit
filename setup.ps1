# ============================================================
# SmartFit v0.0.1
# Windows Development Environment Setup
# ============================================================
#
# This script:
# 1. Determines the SmartFit project root from this file's location.
# 2. Loads the installer modules.
# 3. Verifies the SmartFit project structure.
# 4. Installs/configures Python.
# 5. Installs/configures PostgreSQL.
# 6. Configures the backend environment.
# 7. Installs backend dependencies.
# 8. Verifies the MediaPipe model.
# 9. Initializes the development and test databases.
# 10. Runs the backend automated tests.
# 11. Installs/configures Node.js and npm.
# 12. Installs frontend dependencies.
# 13. Builds the frontend.
# 14. Performs final installation verification.
#
# Exit codes:
# 0  - Successful setup
# 10 - Project structure failure
# 20 - Python setup failure
# 21 - winget failure
# 30 - PostgreSQL installation failure
# 31 - PostgreSQL authentication/connection failure
# 32 - Database creation failure
# 40 - Environment configuration failure
# 50 - Backend setup failure
# 51 - MediaPipe model failure
# 52 - Database initialization failure
# 53 - Backend test failure
# 60 - Node.js installation failure
# 61 - Frontend setup failure
# 99 - Unknown setup failure
# ============================================================

[CmdletBinding()]
param ()

# ------------------------------------------------------------
# Project root
# ------------------------------------------------------------
#
# setup.ps1 is located at the root of the SmartFit repository.
# Using $PSScriptRoot makes the installer independent of the
# location from which the repository was cloned.
# ------------------------------------------------------------

$ProjectRoot = $PSScriptRoot

# ------------------------------------------------------------
# Installer module paths
# ------------------------------------------------------------

$WindowsInstallerRoot = Join-Path `
    $ProjectRoot `
    "installer\windows"

$ModulesRoot = Join-Path `
    $WindowsInstallerRoot `
    "modules"

$LoggingModule = Join-Path `
    $ModulesRoot `
    "Logging.ps1"

$PythonModule = Join-Path `
    $ModulesRoot `
    "Python.ps1"

$PostgreSQLModule = Join-Path `
    $ModulesRoot `
    "PostgreSQL.ps1"

$BackendModule = Join-Path `
    $ModulesRoot `
    "Backend.ps1"

$FrontendModule = Join-Path `
    $ModulesRoot `
    "Frontend.ps1"

$VerificationModule = Join-Path `
    $ModulesRoot `
    "Verification.ps1"

# ------------------------------------------------------------
# Exit codes
# ------------------------------------------------------------

$EXIT_PROJECT_STRUCTURE = 10
$EXIT_UNKNOWN = 99

# ------------------------------------------------------------
# Verify the installer module directory before loading modules
# ------------------------------------------------------------

if (-not (Test-Path $ModulesRoot -PathType Container)) {
    Write-Error `
        "SmartFit installer modules directory was not found: $ModulesRoot"

    exit $EXIT_PROJECT_STRUCTURE
}

# ------------------------------------------------------------
# Load logging first
# ------------------------------------------------------------
#
# Logging.ps1 intentionally does NOT calculate $ProjectRoot.
# The root project script defines it and the remaining modules
# use that shared variable.
# ------------------------------------------------------------

if (-not (Test-Path $LoggingModule -PathType Leaf)) {
    Write-Error `
        "Required installer module was not found: $LoggingModule"

    exit $EXIT_PROJECT_STRUCTURE
}

. $LoggingModule

# ------------------------------------------------------------
# Display setup information
# ------------------------------------------------------------

Write-Section "SmartFit v0.0.1 Windows Setup"

Write-Info "SmartFit project root: $ProjectRoot"
Write-Info "Installer modules: $ModulesRoot"

# ------------------------------------------------------------
# Load remaining modules
# ------------------------------------------------------------

$RequiredModules = @(
    @{
        Path = $PythonModule
        Description = "Python installer module"
    },
    @{
        Path = $PostgreSQLModule
        Description = "PostgreSQL installer module"
    },
    @{
        Path = $BackendModule
        Description = "backend installer module"
    },
    @{
        Path = $FrontendModule
        Description = "frontend installer module"
    },
    @{
        Path = $VerificationModule
        Description = "verification module"
    }
)

foreach ($RequiredModule in $RequiredModules) {
    if (-not (Test-Path $RequiredModule.Path -PathType Leaf)) {
        Write-SetupFailure `
            -Message "Required $($RequiredModule.Description) was not found: $($RequiredModule.Path)" `
            -ExitCode $EXIT_PROJECT_STRUCTURE
    }

    . $RequiredModule.Path
}

# ------------------------------------------------------------
# Main setup procedure
# ------------------------------------------------------------

try {
    Write-Section "Project Structure"

    $RequiredProjectPaths = @(
        @{
            Path = Join-Path $ProjectRoot "backend"
            Description = "backend directory"
            Type = "Container"
        },
        @{
            Path = Join-Path $ProjectRoot "frontend"
            Description = "frontend directory"
            Type = "Container"
        },
        @{
            Path = Join-Path $ProjectRoot "backend\app"
            Description = "backend app directory"
            Type = "Container"
        },
        @{
            Path = Join-Path $ProjectRoot "backend\models"
            Description = "backend models directory"
            Type = "Container"
        },
        @{
            Path = Join-Path $ProjectRoot "backend\tests"
            Description = "backend tests directory"
            Type = "Container"
        },
        @{
            Path = Join-Path $ProjectRoot "backend\requirements.txt"
            Description = "backend requirements.txt"
            Type = "File"
        },
        @{
            Path = Join-Path $ProjectRoot "frontend\package.json"
            Description = "frontend package.json"
            Type = "File"
        }
    )

    foreach ($RequiredProjectPath in $RequiredProjectPaths) {
        if ($RequiredProjectPath.Type -eq "File") {
            $PathExists = Test-Path `
                $RequiredProjectPath.Path `
                -PathType Leaf
        }
        else {
            $PathExists = Test-Path `
                $RequiredProjectPath.Path `
                -PathType Container
        }

        if (-not $PathExists) {
            Write-SetupFailure `
                -Message "Required SmartFit $($RequiredProjectPath.Description) was not found: $($RequiredProjectPath.Path)" `
                -ExitCode $EXIT_PROJECT_STRUCTURE
        }
    }

    Write-Success "SmartFit project structure verified."

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    Initialize-Python

    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------

    Initialize-PostgreSQL

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    Initialize-Backend

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    Initialize-Frontend

    # --------------------------------------------------------
    # Final verification
    # --------------------------------------------------------

    Test-SmartFitInstallation

    # --------------------------------------------------------
    # Successful completion
    # --------------------------------------------------------

    Write-Information "" -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information "SmartFit v0.0.1 setup completed successfully." -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information "" -InformationAction Continue

    Write-Success "SmartFit development environment is ready."
    Write-Info "Project root: $ProjectRoot"
    Write-Info "Backend: $ProjectRoot\backend"
    Write-Info "Frontend: $ProjectRoot\frontend"

    exit 0
}
catch {
    Write-Information "" -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information "SmartFit setup terminated unexpectedly." -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue

    Write-Error $_.Exception.Message

    exit $EXIT_UNKNOWN
}