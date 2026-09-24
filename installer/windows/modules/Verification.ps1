# ============================================================
# SmartFit v0.0.1
# Installation Verification
# ============================================================
#
# This module:
# 1. Verifies the SmartFit project structure.
# 2. Verifies the backend virtual environment.
# 3. Verifies the MediaPipe model.
# 4. Verifies backend and frontend environment files.
# 5. Verifies frontend dependencies.
# 6. Verifies the frontend production build.
# 7. Displays the final SmartFit installation status.
# ============================================================

$VerificationBackendRoot = Join-Path $ProjectRoot "backend"
$VerificationFrontendRoot = Join-Path $ProjectRoot "frontend"

$VerificationBackendEnv = Join-Path $VerificationBackendRoot ".env"
$VerificationFrontendEnv = Join-Path $VerificationFrontendRoot ".env"

$VerificationVenvPython = Join-Path `
    $VerificationBackendRoot `
    ".venv\Scripts\python.exe"

$VerificationPoseModel = Join-Path `
    $VerificationBackendRoot `
    "models\pose_landmarker_lite.task"

$VerificationFrontendNodeModules = Join-Path `
    $VerificationFrontendRoot `
    "node_modules"

$VerificationFrontendDist = Join-Path `
    $VerificationFrontendRoot `
    "dist"

$VerificationFrontendPackage = Join-Path `
    $VerificationFrontendRoot `
    "package.json"

$EXIT_BACKEND_SETUP = 50
$EXIT_MODEL = 51
$EXIT_FRONTEND = 61


function Test-EnvironmentFile {
    [CmdletBinding()]
    [OutputType([bool])]
    param (
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if (-not (Test-Path $FilePath -PathType Leaf)) {
        Write-Failure "Missing $Description`: $FilePath"
        return $false
    }

    $FileItem = Get-Item $FilePath -ErrorAction SilentlyContinue

    if (-not $FileItem -or $FileItem.Length -le 0) {
        Write-Failure "The $Description is empty: $FilePath"
        return $false
    }

    Write-Success "$Description verified."
    return $true
}


function Test-BackendInstallation {
    [CmdletBinding()]
    param ()

    Write-Step "Verifying the SmartFit backend installation."

    if (-not (Test-Path $VerificationBackendRoot -PathType Container)) {
        Write-SetupFailure `
            -Message "The backend directory was not found: $VerificationBackendRoot" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    if (-not (Test-Path $VerificationVenvPython -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The backend Python virtual environment was not found: $VerificationVenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    Write-Success "Backend Python environment verified."

    if (-not (Test-Path $VerificationPoseModel -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The MediaPipe pose landmark model was not found: $VerificationPoseModel" `
            -ExitCode $EXIT_MODEL
    }

    $ModelItem = Get-Item $VerificationPoseModel -ErrorAction SilentlyContinue

    if (-not $ModelItem -or $ModelItem.Length -le 0) {
        Write-SetupFailure `
            -Message "The MediaPipe pose landmark model is missing or empty." `
            -ExitCode $EXIT_MODEL
    }

    Write-Success "MediaPipe pose landmark model verified."

    $BackendEnvironmentValid = Test-EnvironmentFile `
        -FilePath $VerificationBackendEnv `
        -Description "backend .env file"

    if (-not $BackendEnvironmentValid) {
        Write-SetupFailure `
            -Message "The backend environment file could not be verified." `
            -ExitCode $EXIT_BACKEND_SETUP
    }
}


function Test-FrontendInstallation {
    [CmdletBinding()]
    param ()

    Write-Step "Verifying the SmartFit frontend installation."

    if (-not (Test-Path $VerificationFrontendRoot -PathType Container)) {
        Write-SetupFailure `
            -Message "The frontend directory was not found: $VerificationFrontendRoot" `
            -ExitCode $EXIT_FRONTEND
    }

    if (-not (Test-Path $VerificationFrontendPackage -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The frontend package.json file was not found: $VerificationFrontendPackage" `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Frontend package.json verified."

    if (-not (Test-Path $VerificationFrontendNodeModules -PathType Container)) {
        Write-SetupFailure `
            -Message "The frontend node_modules directory was not found: $VerificationFrontendNodeModules" `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Frontend dependencies verified."

    if (-not (Test-Path $VerificationFrontendDist -PathType Container)) {
        Write-SetupFailure `
            -Message "The frontend production build directory was not found: $VerificationFrontendDist" `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Frontend production build verified."

    if (Test-Path $VerificationFrontendEnv -PathType Leaf) {
        $FrontendEnvironmentValid = Test-EnvironmentFile `
            -FilePath $VerificationFrontendEnv `
            -Description "frontend .env file"

        if (-not $FrontendEnvironmentValid) {
            Write-WarningMessage "The frontend .env file exists but could not be verified."
        }
    }
    else {
        Write-Info "No frontend .env file was found. This is acceptable if the frontend uses its configured defaults."
    }
}


function Test-CommandAvailability {
    [CmdletBinding()]
    param ()

    Write-Step "Verifying required development commands."

    $RequiredCommands = @(
        "python",
        "node",
        "npm"
    )

    foreach ($CommandName in $RequiredCommands) {
        if (-not (Test-CommandExistence $CommandName)) {
            Write-SetupFailure `
                -Message "Required command was not found: $CommandName" `
                -ExitCode $EXIT_BACKEND_SETUP
        }

        Write-Success "$CommandName is available."
    }
}


function Test-SmartFitInstallation {
    [CmdletBinding()]
    param ()

    Write-Section "Final Installation Verification"

    Test-CommandAvailability
    Test-BackendInstallation
    Test-FrontendInstallation

    Write-Information "" -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information "SmartFit v0.0.1 installation verification completed." -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information "" -InformationAction Continue

    Write-Success "SmartFit development environment is ready."
}