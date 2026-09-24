# ============================================================
# SmartFit v0.0.1
# Backend Installer
# ============================================================
#
# This module:
# 1. Verifies the backend project structure.
# 2. Verifies the Python virtual environment.
# 3. Installs backend Python dependencies.
# 4. Verifies the MediaPipe pose model.
# 5. Initializes the SmartFit development and test databases.
# 6. Runs the complete backend automated test suite.
#
# Exit codes:
# 50 - Backend setup failure
# 51 - MediaPipe model failure
# 52 - Database initialization failure
# 53 - Backend test failure
# ============================================================

$BackendRoot = Join-Path $ProjectRoot "backend"
$BackendAppRoot = Join-Path $BackendRoot "app"
$BackendModelsRoot = Join-Path $BackendRoot "models"
$BackendScriptsRoot = Join-Path $BackendRoot "scripts"
$BackendTestsRoot = Join-Path $BackendRoot "tests"

$BackendRequirementsFile = Join-Path $BackendRoot "requirements.txt"
$PoseModelFile = Join-Path $BackendModelsRoot "pose_landmarker_lite.task"

$VenvPath = Join-Path $BackendRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

$EXIT_BACKEND_SETUP = 50
$EXIT_MODEL = 51
$EXIT_DATABASE = 52
$EXIT_TESTS = 53


function Test-BackendStructure {
    [CmdletBinding()]
    param ()

    Write-Step "Checking the SmartFit backend project structure."

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
            if (-not (Test-Path $RequiredPath.Path -PathType Leaf)) {
                Write-SetupFailure `
                    -Message "Required $($RequiredPath.Description) was not found: $($RequiredPath.Path)" `
                    -ExitCode $EXIT_BACKEND_SETUP
            }
        }
        else {
            if (-not (Test-Path $RequiredPath.Path -PathType Container)) {
                Write-SetupFailure `
                    -Message "Required $($RequiredPath.Description) was not found: $($RequiredPath.Path)" `
                    -ExitCode $EXIT_BACKEND_SETUP
            }
        }
    }

    Write-Success "Backend project structure is valid."
}


function Install-BackendDependency {
    [CmdletBinding()]
    param ()

    Write-Section "Backend Dependencies"

    if (-not (Test-Path $BackendRequirementsFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The backend requirements.txt file was not found: $BackendRequirementsFile" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    $RequirementsExitCode = 1

    Write-Step "Installing SmartFit backend Python dependencies."

    $OriginalLocation = (Get-Location).Path

    try {
        Set-Location $BackendRoot

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pip install -r requirements.txt"

        & $VenvPython -m pip install -r $BackendRequirementsFile

        $RequirementsExitCode = [int]$LASTEXITCODE
    }
    catch {
        $RequirementsExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }

    Write-CommandFooter -ExitCode $RequirementsExitCode

    if ($RequirementsExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Backend Python dependency installation failed." `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    Write-Success "Backend Python dependencies installed."
}


function Test-PoseModel {
    [CmdletBinding()]
    param ()

    Write-Section "Computer Vision Model"

    if (-not (Test-Path $PoseModelFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The MediaPipe pose landmark model was not found: $PoseModelFile" `
            -ExitCode $EXIT_MODEL
    }

    $ModelItem = Get-Item $PoseModelFile -ErrorAction SilentlyContinue

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

    Write-Success "MediaPipe pose landmark model is available."
    Write-Info "Model: $PoseModelFile"
    Write-Info "Model size: $($ModelItem.Length) bytes"
}


function Initialize-SmartFitDatabase {
    [CmdletBinding()]
    param ()

    Write-Section "SmartFit Database Initialization"

    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_DATABASE
    }

    $ResetExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Initializing the SmartFit development and test databases."

    try {
        Set-Location $BackendRoot

        Write-CommandHeader ".\.venv\Scripts\python.exe -m scripts.reset_databases --target both"

        & $VenvPython -m scripts.reset_databases --target both

        $ResetExitCode = [int]$LASTEXITCODE
    }
    catch {
        $ResetExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }

    Write-CommandFooter -ExitCode $ResetExitCode

    if ($ResetExitCode -ne 0) {
        Write-SetupFailure `
            -Message "SmartFit database initialization failed." `
            -ExitCode $EXIT_DATABASE
    }

    Write-Success "SmartFit development and test databases initialized."
    Write-Info "Development database: SmartFit_db"
    Write-Info "Test database: SmartFit_Test_db"
}


function Invoke-BackendTest {
    [CmdletBinding()]
    param ()

    Write-Section "Backend Tests"

    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_TESTS
    }

    $TestExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Running the SmartFit backend automated test suite."

    try {
        Set-Location $BackendRoot

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pytest"

        & $VenvPython -m pytest

        $TestExitCode = [int]$LASTEXITCODE
    }
    catch {
        $TestExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }

    Write-CommandFooter -ExitCode $TestExitCode

    if ($TestExitCode -ne 0) {
        Write-SetupFailure `
            -Message "SmartFit backend automated tests failed." `
            -ExitCode $EXIT_TESTS
    }

    Write-Success "All SmartFit backend automated tests passed."
}


function Initialize-Backend {
    [CmdletBinding()]
    param ()

    Write-Section "Backend Setup"

    Test-BackendStructure
    Install-BackendDependency
    Test-PoseModel
    Initialize-SmartFitDatabase
    Invoke-BackendTest

    Write-Success "SmartFit backend setup completed successfully."
}