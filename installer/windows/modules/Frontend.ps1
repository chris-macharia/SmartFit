# ============================================================
# SmartFit v0.0.1
# Frontend Installer
# ============================================================
#
# This module:
# 1. Verifies Node.js and npm.
# 2. Installs Node.js using winget when required.
# 3. Installs frontend npm dependencies.
# 4. Builds the React/Vite frontend.
#
# Exit codes:
# 60 - Node.js installation failure
# 61 - Frontend setup failure
# ============================================================

$FrontendRoot = Join-Path $ProjectRoot "frontend"
$FrontendPackageFile = Join-Path $FrontendRoot "package.json"
$FrontendNodeModules = Join-Path $FrontendRoot "node_modules"

$NodeWingetId = "OpenJS.NodeJS.LTS"

$EXIT_NODE = 60
$EXIT_FRONTEND = 61


function Find-Node {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    $NodeCommand = Get-Command "node" -ErrorAction SilentlyContinue

    if (-not $NodeCommand) {
        return $null
    }

    try {
        $NodeVersion = & node --version 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Info "Detected Node.js: $NodeVersion"
            return "node"
        }
    }
    catch {
        return $null
    }

    return $null
}


function Find-Npm {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    $NpmCommand = Get-Command "npm" -ErrorAction SilentlyContinue

    if (-not $NpmCommand) {
        return $null
    }

    try {
        $NpmVersion = & npm --version 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Info "Detected npm: $NpmVersion"
            return "npm"
        }
    }
    catch {
        return $null
    }

    return $null
}


function Install-Node {
    [CmdletBinding()]
    param ()

    Write-Step "Node.js was not found. Preparing installation."

    if (-not (Test-CommandExistence "winget")) {
        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install Node.js automatically." `
            -ExitCode $EXIT_NODE
    }

    $WingetExitCode = 1

    Write-Info "Installing Node.js LTS using winget."
    Write-CommandHeader "winget install --id $NodeWingetId --exact --source winget"

    try {
        & winget install --id $NodeWingetId --exact --source winget

        $WingetExitCode = [int]$LASTEXITCODE
    }
    catch {
        $WingetExitCode = 1
    }

    Write-CommandFooter -ExitCode $WingetExitCode

    if ($WingetExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Node.js installation failed through winget." `
            -ExitCode $EXIT_NODE
    }

    Initialize-ProcessPath

    $DetectedNode = Find-Node
    $DetectedNpm = Find-Npm

    if (-not $DetectedNode -or -not $DetectedNpm) {
        Write-SetupFailure `
            -Message "Node.js was installed, but node and npm could not be detected afterwards." `
            -ExitCode $EXIT_NODE
    }

    Write-Success "Node.js and npm are available."
}


function Install-FrontendDependency {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Dependencies"

    if (-not (Test-Path $FrontendPackageFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The frontend package.json file was not found: $FrontendPackageFile" `
            -ExitCode $EXIT_FRONTEND
    }

    if (-not (Test-CommandExistence "npm")) {
        Write-SetupFailure `
            -Message "npm was not found. Node.js must be installed before frontend dependencies can be installed." `
            -ExitCode $EXIT_NODE
    }

    $NpmExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Installing SmartFit frontend npm dependencies."

    try {
        Set-Location $FrontendRoot

        Write-CommandHeader "npm install"

        & npm install

        $NpmExitCode = [int]$LASTEXITCODE
    }
    catch {
        $NpmExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }

    Write-CommandFooter -ExitCode $NpmExitCode

    if ($NpmExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Frontend npm dependency installation failed." `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Frontend npm dependencies installed."
}


function Invoke-FrontendBuild {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Build"

    if (-not (Test-Path $FrontendPackageFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The frontend package.json file was not found: $FrontendPackageFile" `
            -ExitCode $EXIT_FRONTEND
    }

    if (-not (Test-Path $FrontendNodeModules -PathType Container)) {
        Write-SetupFailure `
            -Message "Frontend dependencies are not installed. The node_modules directory was not found." `
            -ExitCode $EXIT_FRONTEND
    }

    $BuildExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Building the SmartFit React/Vite frontend."

    try {
        Set-Location $FrontendRoot

        Write-CommandHeader "npm run build"

        & npm run build

        $BuildExitCode = [int]$LASTEXITCODE
    }
    catch {
        $BuildExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }

    Write-CommandFooter -ExitCode $BuildExitCode

    if ($BuildExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Frontend build failed." `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "SmartFit frontend build completed successfully."
}


function Initialize-Frontend {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Setup"

    $DetectedNode = Find-Node
    $DetectedNpm = Find-Npm

    if (-not $DetectedNode -or -not $DetectedNpm) {
        Install-Node
    }
    else {
        Write-Success "Node.js and npm are already available."
    }

    Initialize-ProcessPath

    if (-not (Test-CommandExistence "node")) {
        Write-SetupFailure `
            -Message "Node.js is not available in the current PowerShell session." `
            -ExitCode $EXIT_NODE
    }

    if (-not (Test-CommandExistence "npm")) {
        Write-SetupFailure `
            -Message "npm is not available in the current PowerShell session." `
            -ExitCode $EXIT_NODE
    }

    Install-FrontendDependency
    Invoke-FrontendBuild

    Write-Success "SmartFit frontend setup completed successfully."
}