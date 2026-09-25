# ============================================================
# SmartFit v0.0.1
# Windows Installer - Backend Module
# ============================================================
#
# This module:
#
# 1. Verifies the backend project structure.
# 2. Verifies the Python virtual environment.
# 3. Installs backend Python dependencies.
# 4. Verifies the bundled MediaPipe Pose Landmarker model.
# 5. Verifies the PostgreSQL environment configuration.
# 6. Initializes the SmartFit development and test databases.
# 7. Runs the complete backend automated test suite.
#
# PostgreSQL installation and configuration are handled by
# PostgreSQL.ps1.
#
# This module deliberately does NOT modify app/core/config.py
# or app/db/database.py.
#
# Exit codes:
# 50 - Backend setup failure
# 51 - MediaPipe model failure
# 52 - Database initialization failure
# 53 - Backend test failure
# ============================================================


# ============================================================
# Backend Paths
# ============================================================

$BackendRoot = Join-Path `
    $ProjectRoot `
    "backend"

$BackendAppRoot = Join-Path `
    $BackendRoot `
    "app"

$BackendModelsRoot = Join-Path `
    $BackendRoot `
    "models"

$BackendScriptsRoot = Join-Path `
    $BackendRoot `
    "scripts"

$BackendTestsRoot = Join-Path `
    $BackendRoot `
    "tests"


$BackendRequirementsFile = Join-Path `
    $BackendRoot `
    "requirements.txt"


$BackendEnvFile = Join-Path `
    $BackendRoot `
    ".env"


$PoseModelFile = Join-Path `
    $BackendModelsRoot `
    "pose_landmarker_lite.task"


$VenvPath = Join-Path `
    $BackendRoot `
    ".venv"

$VenvPython = Join-Path `
    $VenvPath `
    "Scripts\python.exe"


# ============================================================
# Exit Codes
# ============================================================

$EXIT_BACKEND_SETUP = 50

$EXIT_MODEL = 51

$EXIT_DATABASE = 52

$EXIT_TESTS = 53


# ============================================================
# Backend Structure Verification
# ============================================================

function Test-BackendStructure {
    [CmdletBinding()]
    param ()


    Write-Step `
        "Checking the SmartFit backend project structure."


    $RequiredPaths = @(
        @{
            Path = $BackendRoot
            Description = "backend directory"
            Type = "Container"
        },
        @{
            Path = $BackendAppRoot
            Description = "backend app directory"
            Type = "Container"
        },
        @{
            Path = $BackendModelsRoot
            Description = "backend models directory"
            Type = "Container"
        },
        @{
            Path = $BackendScriptsRoot
            Description = "backend scripts directory"
            Type = "Container"
        },
        @{
            Path = $BackendTestsRoot
            Description = "backend tests directory"
            Type = "Container"
        },
        @{
            Path = $BackendRequirementsFile
            Description = "backend requirements.txt"
            Type = "File"
        }
    )


    foreach ($RequiredPath in $RequiredPaths) {

        if ($RequiredPath.Type -eq "File") {

            if (-not (Test-Path `
                $RequiredPath.Path `
                -PathType Leaf)) {

                Write-SetupFailure `
                    -Message "Required $($RequiredPath.Description) was not found: $($RequiredPath.Path)" `
                    -ExitCode $EXIT_BACKEND_SETUP
            }
        }
        else {

            if (-not (Test-Path `
                $RequiredPath.Path `
                -PathType Container)) {

                Write-SetupFailure `
                    -Message "Required $($RequiredPath.Description) was not found: $($RequiredPath.Path)" `
                    -ExitCode $EXIT_BACKEND_SETUP
            }
        }
    }


    Write-Success `
        "Backend project structure is valid."
}


# ============================================================
# Install Backend Dependencies
# ============================================================

function Install-BackendDependency {
    [CmdletBinding()]
    param ()


    Write-Section "Backend Dependencies"


    if (-not (Test-Path `
        $BackendRequirementsFile `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend requirements.txt file was not found: $BackendRequirementsFile" `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    if (-not (Test-Path `
        $VenvPython `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    $RequirementsExitCode = 1


    Write-Step `
        "Installing SmartFit backend Python dependencies."


    $OriginalLocation = (Get-Location).Path


    try {

        Set-Location $BackendRoot


        Write-CommandHeader `
            ".\.venv\Scripts\python.exe -m pip install -r requirements.txt"


        & $VenvPython `
            -m pip `
            install `
            -r $BackendRequirementsFile


        $RequirementsExitCode = [int]$LASTEXITCODE
    }
    catch {

        $RequirementsExitCode = 1
    }
    finally {

        Set-Location $OriginalLocation
    }


    Write-CommandFooter `
        -ExitCode $RequirementsExitCode


    if ($RequirementsExitCode -ne 0) {

        Write-SetupFailure `
            -Message "Backend Python dependency installation failed." `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    Write-Success `
        "Backend Python dependencies installed."
}


# ============================================================
# Verify MediaPipe Pose Landmarker Model
# ============================================================

function Test-PoseModel {
    [CmdletBinding()]
    param ()


    Write-Section "Computer Vision Model"


    if (-not (Test-Path `
        $PoseModelFile `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The bundled MediaPipe pose landmark model was not found: $PoseModelFile" `
            -ExitCode $EXIT_MODEL
    }


    $ModelItem = Get-Item `
        $PoseModelFile `
        -ErrorAction SilentlyContinue


    if (-not $ModelItem) {

        Write-SetupFailure `
            -Message "Unable to inspect the MediaPipe pose landmark model: $PoseModelFile" `
            -ExitCode $EXIT_MODEL
    }


    if ($ModelItem.Length -le 0) {

        Write-SetupFailure `
            -Message "The MediaPipe pose landmark model is empty: $PoseModelFile" `
            -ExitCode $EXIT_MODEL
    }


    Write-Success `
        "Bundled MediaPipe pose landmark model is available."


    Write-Info `
        "Model: $PoseModelFile"

    Write-Info `
        "Model size: $($ModelItem.Length) bytes"
}


# ============================================================
# Read a value from the backend .env file
# ============================================================
#
# This function intentionally returns only the requested value.
#
# It is used for configuration validation.
#
# Password values are never printed by this module.
# ============================================================

function Get-BackendEnvValue {
    [CmdletBinding()]
    [OutputType([string])]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Key
    )


    if (-not (Test-Path `
        $BackendEnvFile `
        -PathType Leaf)) {

        return $null
    }


    try {

        $EnvironmentContent = Get-Content `
            -Path $BackendEnvFile `
            -Raw `
            -ErrorAction Stop
    }
    catch {

        return $null
    }


    $Pattern = "(?m)^\s*$([regex]::Escape($Key))\s*=\s*(.*?)\s*$"


    $Match = [regex]::Match(
        $EnvironmentContent,
        $Pattern
    )


    if (-not $Match.Success) {

        return $null
    }


    return $Match.Groups[1].Value.Trim()
}


# ============================================================
# Verify Backend Database Environment
# ============================================================
#
# PostgreSQL.ps1 is responsible for creating/updating .env.
#
# This function verifies that the backend receives the expected
# database configuration before Python imports the application.
#
# This is deliberately performed BEFORE reset_databases.py.
# ============================================================

function Test-BackendDatabaseEnvironment {
    [CmdletBinding()]
    param ()


    Write-Section "Backend Database Configuration"


    # --------------------------------------------------------
    # Verify backend .env exists.
    # --------------------------------------------------------

    if (-not (Test-Path `
        $BackendEnvFile `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend .env file was not found: $BackendEnvFile. PostgreSQL configuration must complete before backend database initialization." `
            -ExitCode $EXIT_DATABASE
    }


    Write-Info `
        "Backend environment file found: $BackendEnvFile"


    # --------------------------------------------------------
    # Retrieve database values from .env.
    # --------------------------------------------------------

    $DotEnvDatabaseUrl = Get-BackendEnvValue `
        -Key "DATABASE_URL"

    $DotEnvTestDatabaseUrl = Get-BackendEnvValue `
        -Key "TEST_DATABASE_URL"

    $DotEnvPostgresUser = Get-BackendEnvValue `
        -Key "POSTGRES_USER"

    $DotEnvPostgresHost = Get-BackendEnvValue `
        -Key "POSTGRES_HOST"

    $DotEnvPostgresPort = Get-BackendEnvValue `
        -Key "POSTGRES_PORT"

    $DotEnvPostgresDatabase = Get-BackendEnvValue `
        -Key "POSTGRES_DB"


    # --------------------------------------------------------
    # Check required values.
    # --------------------------------------------------------

    if ([string]::IsNullOrWhiteSpace($DotEnvDatabaseUrl)) {

        Write-SetupFailure `
            -Message "DATABASE_URL is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($DotEnvTestDatabaseUrl)) {

        Write-SetupFailure `
            -Message "TEST_DATABASE_URL is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($DotEnvPostgresUser)) {

        Write-SetupFailure `
            -Message "POSTGRES_USER is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($DotEnvPostgresHost)) {

        Write-SetupFailure `
            -Message "POSTGRES_HOST is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($DotEnvPostgresPort)) {

        Write-SetupFailure `
            -Message "POSTGRES_PORT is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($DotEnvPostgresDatabase)) {

        Write-SetupFailure `
            -Message "POSTGRES_DB is missing or empty in backend/.env." `
            -ExitCode $EXIT_DATABASE
    }


    # --------------------------------------------------------
    # Validate PostgreSQL URL structure.
    #
    # We deliberately do not print the complete URL because it
    # contains the PostgreSQL password.
    # --------------------------------------------------------

    $DevelopmentUrlPattern = `
        "^postgresql://[^:]+:.+@[^:]+:\d+/.+$"

    $TestUrlPattern = `
        "^postgresql://[^:]+:.+@[^:]+:\d+/.+$"


    if ($DotEnvDatabaseUrl -notmatch $DevelopmentUrlPattern) {

        Write-SetupFailure `
            -Message "DATABASE_URL in backend/.env is not a valid PostgreSQL SQLAlchemy connection URL." `
            -ExitCode $EXIT_DATABASE
    }


    if ($DotEnvTestDatabaseUrl -notmatch $TestUrlPattern) {

        Write-SetupFailure `
            -Message "TEST_DATABASE_URL in backend/.env is not a valid PostgreSQL SQLAlchemy connection URL." `
            -ExitCode $EXIT_DATABASE
    }


    # --------------------------------------------------------
    # Verify the values inherited by the current installer
    # process.
    #
    # PostgreSQL.ps1 synchronizes these values after writing
    # .env. Child Python processes inherit them.
    # --------------------------------------------------------

    if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {

        Write-SetupFailure `
            -Message "DATABASE_URL is not available in the installer process environment." `
            -ExitCode $EXIT_DATABASE
    }


    if ([string]::IsNullOrWhiteSpace($env:TEST_DATABASE_URL)) {

        Write-SetupFailure `
            -Message "TEST_DATABASE_URL is not available in the installer process environment." `
            -ExitCode $EXIT_DATABASE
    }


    # --------------------------------------------------------
    # Verify the process values match .env.
    #
    # This is the critical check for the original SQLAlchemy
    # failure.
    # --------------------------------------------------------

    if ($env:DATABASE_URL -ne $DotEnvDatabaseUrl) {

        Write-SetupFailure `
            -Message "The installer DATABASE_URL does not match backend/.env. The Python backend would receive inconsistent database configuration." `
            -ExitCode $EXIT_DATABASE
    }


    if ($env:TEST_DATABASE_URL -ne $DotEnvTestDatabaseUrl) {

        Write-SetupFailure `
            -Message "The installer TEST_DATABASE_URL does not match backend/.env. The Python backend would receive inconsistent database configuration." `
            -ExitCode $EXIT_DATABASE
    }


    # --------------------------------------------------------
    # Display safe diagnostics.
    #
    # Never display the complete URLs because they contain the
    # PostgreSQL password.
    # --------------------------------------------------------

    Write-Success `
        "Backend PostgreSQL configuration is valid."


    Write-Info `
        "Development database URL: present and valid"

    Write-Info `
        "Test database URL: present and valid"

    Write-Info `
        "PostgreSQL user: $DotEnvPostgresUser"

    Write-Info `
        "PostgreSQL host: $DotEnvPostgresHost"

    Write-Info `
        "PostgreSQL port: $DotEnvPostgresPort"

    Write-Info `
        "Development database: $DotEnvPostgresDatabase"

    Write-Info `
        "Installer database environment: synchronized"


    return $true
}


# ============================================================
# Initialize SmartFit Databases
# ============================================================

function Initialize-SmartFitDatabase {
    [CmdletBinding()]
    param ()


    Write-Section `
        "SmartFit Database Initialization"


    if (-not (Test-Path `
        $VenvPython `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_DATABASE
    }


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Validate the environment BEFORE Python imports
    # app.db.database.
    # --------------------------------------------------------

    Test-BackendDatabaseEnvironment


    $ResetExitCode = 1

    $OriginalLocation = (Get-Location).Path


    Write-Step `
        "Initializing the SmartFit development and test databases."


    try {

        Set-Location $BackendRoot


        Write-CommandHeader `
            ".\.venv\Scripts\python.exe -m scripts.reset_databases --target both"


        # ----------------------------------------------------
        # Python inherits DATABASE_URL and TEST_DATABASE_URL
        # from the current PowerShell process.
        # ----------------------------------------------------

        & $VenvPython `
            -m scripts.reset_databases `
            --target both


        $ResetExitCode = [int]$LASTEXITCODE
    }
    catch {

        $ResetExitCode = 1
    }
    finally {

        Set-Location $OriginalLocation
    }


    Write-CommandFooter `
        -ExitCode $ResetExitCode


    if ($ResetExitCode -ne 0) {

        Write-SetupFailure `
            -Message "SmartFit database initialization failed. The PostgreSQL configuration was verified before Python was started." `
            -ExitCode $EXIT_DATABASE
    }


    Write-Success `
        "SmartFit development and test databases initialized."


    Write-Info `
        "Development database: SmartFit_db"

    Write-Info `
        "Test database: SmartFit_Test_db"
}


# ============================================================
# Run Backend Tests
# ============================================================

function Invoke-BackendTest {
    [CmdletBinding()]
    param ()


    Write-Section "Backend Tests"


    if (-not (Test-Path `
        $VenvPython `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_TESTS
    }


    $TestExitCode = 1

    $OriginalLocation = (Get-Location).Path


    Write-Step `
        "Running the SmartFit backend automated test suite."


    try {

        Set-Location $BackendRoot


        Write-CommandHeader `
            ".\.venv\Scripts\python.exe -m pytest"


        & $VenvPython `
            -m pytest


        $TestExitCode = [int]$LASTEXITCODE
    }
    catch {

        $TestExitCode = 1
    }
    finally {

        Set-Location $OriginalLocation
    }


    Write-CommandFooter `
        -ExitCode $TestExitCode


    if ($TestExitCode -ne 0) {

        Write-SetupFailure `
            -Message "SmartFit backend automated tests failed." `
            -ExitCode $EXIT_TESTS
    }


    Write-Success `
        "All SmartFit backend automated tests passed."
}


# ============================================================
# Main Backend Setup
# ============================================================

function Initialize-Backend {
    [CmdletBinding()]
    param ()


    Write-Section "Backend Setup"


    # --------------------------------------------------------
    # 1. Verify backend structure.
    # --------------------------------------------------------

    Test-BackendStructure


    # --------------------------------------------------------
    # 2. Install Python dependencies.
    # --------------------------------------------------------

    Install-BackendDependency


    # --------------------------------------------------------
    # 3. Verify bundled MediaPipe model.
    # --------------------------------------------------------

    Test-PoseModel


    # --------------------------------------------------------
    # 4. Verify PostgreSQL/.env configuration and initialize
    #    SmartFit databases.
    # --------------------------------------------------------

    Initialize-SmartFitDatabase


    # --------------------------------------------------------
    # 5. Run automated backend tests.
    # --------------------------------------------------------

    Invoke-BackendTest


    Write-Success `
        "SmartFit backend setup completed successfully."
}