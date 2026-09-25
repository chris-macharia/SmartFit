# ============================================================
# SmartFit v0.0.1
# Frontend Installer
# ============================================================
#
# PURPOSE
# -------
# This module prepares and builds the SmartFit React/Vite
# frontend.
#
# RESPONSIBILITIES
# ----------------
# 1. Verify that Node.js is available.
# 2. Verify that npm is available.
# 3. Install Node.js LTS using winget when required.
# 4. Refresh the current PowerShell PATH after installation.
# 5. Verify that frontend/package.json exists.
# 6. Detect whether frontend dependencies already exist.
# 7. Reuse existing dependencies when they are valid.
# 8. Install/update dependencies when they are missing or
#    when the package lock indicates that they need refreshing.
# 9. Build the React/Vite frontend.
# 10. Provide detailed diagnostic output throughout the process.
#
# DEPENDENCY STRATEGY
# -------------------
# If node_modules already exists:
#
#     Existing dependencies
#             |
#             +---- package-lock.json exists
#             |          |
#             |          +---- npm ci --dry-run succeeds
#             |                     |
#             |                     +--> Reuse dependencies
#             |
#             +---- No lockfile / dependency state uncertain
#                        |
#                        +--> npm install
#
# If node_modules does NOT exist:
#
#     package-lock.json exists
#             |
#             +--> npm ci
#
#     package-lock.json does not exist
#             |
#             +--> npm install
#
# This approach avoids unnecessarily downloading dependencies on
# every installer run while still allowing the project to recover
# when dependencies have changed.
#
# EXIT CODES
# ----------
# 60 - Node.js installation/runtime failure
# 61 - Frontend setup/build failure
# ============================================================


# ============================================================
# FRONTEND PATHS
# ============================================================

$FrontendRoot = Join-Path $ProjectRoot "frontend"

$FrontendPackageFile = Join-Path $FrontendRoot "package.json"

$FrontendLockFile = Join-Path $FrontendRoot "package-lock.json"

$FrontendNodeModules = Join-Path $FrontendRoot "node_modules"

$FrontendDist = Join-Path $FrontendRoot "dist"


# ============================================================
# NODE.JS CONFIGURATION
# ============================================================

# Official winget package identifier for the Node.js LTS release.
#
# LTS is intentionally used instead of the Current release because
# SmartFit is an application project and should prioritize a stable,
# supported runtime over the newest Node.js release.
$NodeWingetId = "OpenJS.NodeJS.LTS"


# ============================================================
# EXIT CODES
# ============================================================

$EXIT_NODE = 60
$EXIT_FRONTEND = 61


# ============================================================
# Find-Node
# ============================================================
#
# Attempts to locate the node executable and verifies that it
# can actually execute.
#
# Returns:
#   "node"  -> Node.js is available
#   $null   -> Node.js is unavailable
#
# ============================================================

function Find-Node {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    Write-Info "Checking for Node.js..."

    $NodeCommand = Get-Command "node" -ErrorAction SilentlyContinue

    if (-not $NodeCommand) {
        Write-Info "Node.js executable was not found in PATH."
        return $null
    }

    try {
        $NodeVersion = & node --version 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Info "Detected Node.js: $NodeVersion"
            Write-Info "Node.js executable: $($NodeCommand.Source)"

            return "node"
        }
    }
    catch {
        Write-Info "Node.js was found, but could not be executed."
        return $null
    }

    Write-Info "Node.js version check failed."

    return $null
}


# ============================================================
# Find-Npm
# ============================================================
#
# Attempts to locate npm and verifies that it can execute.
#
# Returns:
#   "npm"  -> npm is available
#   $null  -> npm is unavailable
#
# ============================================================

function Find-Npm {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    Write-Info "Checking for npm..."

    $NpmCommand = Get-Command "npm" -ErrorAction SilentlyContinue

    if (-not $NpmCommand) {
        Write-Info "npm executable was not found in PATH."
        return $null
    }

    try {
        $NpmVersion = & npm --version 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Info "Detected npm: $NpmVersion"
            Write-Info "npm executable: $($NpmCommand.Source)"

            return "npm"
        }
    }
    catch {
        Write-Info "npm was found, but could not be executed."
        return $null
    }

    Write-Info "npm version check failed."

    return $null
}


# ============================================================
# Install-Node
# ============================================================
#
# Installs Node.js LTS using winget.
#
# This function is only called when Node.js/npm cannot be found.
#
# ============================================================

function Install-Node {
    [CmdletBinding()]
    param ()

    Write-Section "Node.js Installation"

    Write-Step "Node.js was not detected."
    Write-Info "SmartFit requires Node.js and npm to build the frontend."
    Write-Info "The installer will attempt to install Node.js LTS automatically."


    # --------------------------------------------------------
    # Verify winget
    # --------------------------------------------------------

    Write-Info "Checking for Windows Package Manager (winget)..."

    if (-not (Test-CommandExistence "winget")) {
        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install Node.js automatically." `
            -ExitCode $EXIT_NODE
    }

    Write-Success "winget is available."


    # --------------------------------------------------------
    # Install Node.js
    # --------------------------------------------------------

    $WingetExitCode = 1

    Write-Step "Installing Node.js LTS."

    Write-Info "Package: $NodeWingetId"
    Write-Info "Source: winget"
    Write-Info "This may take several minutes depending on the system."


    Write-CommandHeader "winget install --id $NodeWingetId --exact --source winget"

    try {
        & winget install `
            --id $NodeWingetId `
            --exact `
            --source winget

        $WingetExitCode = [int]$LASTEXITCODE
    }
    catch {
        Write-Info "An exception occurred while running winget."
        Write-Info $_.Exception.Message

        $WingetExitCode = 1
    }

    Write-CommandFooter -ExitCode $WingetExitCode


    # --------------------------------------------------------
    # Verify installation result
    # --------------------------------------------------------

    if ($WingetExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Node.js installation failed through winget." `
            -ExitCode $EXIT_NODE
    }

    Write-Success "Node.js installation command completed."


    # --------------------------------------------------------
    # Refresh PATH
    # --------------------------------------------------------

    Write-Step "Refreshing the current PowerShell PATH."

    Initialize-ProcessPath

    Write-Info "PATH refresh completed."


    # --------------------------------------------------------
    # Verify Node.js and npm
    # --------------------------------------------------------

    Write-Step "Verifying the newly installed Node.js environment."

    $DetectedNode = Find-Node
    $DetectedNpm = Find-Npm

    if (-not $DetectedNode -or -not $DetectedNpm) {
        Write-SetupFailure `
            -Message "Node.js was installed, but node and npm could not be detected afterwards. A new PowerShell session may be required." `
            -ExitCode $EXIT_NODE
    }

    Write-Success "Node.js and npm are available."
}


# ============================================================
# Test-NpmDependencies
# ============================================================
#
# Determines whether the existing node_modules directory can
# be reused safely.
#
# The function intentionally does NOT delete node_modules.
#
# When package-lock.json exists, npm is asked to perform a
# dry-run of the lockfile installation. This allows us to detect
# whether the current dependency state is compatible with the
# lockfile without actually reinstalling everything.
#
# Returns:
#   $true  -> dependencies can be reused
#   $false -> dependencies should be installed/refreshed
#
# ============================================================

function Test-NpmDependencies {
    [CmdletBinding()]
    [OutputType([bool])]
    param ()

    Write-Step "Checking existing frontend dependencies."


    # --------------------------------------------------------
    # node_modules does not exist
    # --------------------------------------------------------

    if (-not (Test-Path $FrontendNodeModules -PathType Container)) {
        Write-Info "node_modules directory was not found."
        Write-Info "Frontend dependencies need to be installed."

        return $false
    }


    Write-Info "Existing node_modules directory detected:"
    Write-Info "  $FrontendNodeModules"


    # --------------------------------------------------------
    # package-lock.json exists
    # --------------------------------------------------------

    if (Test-Path $FrontendLockFile -PathType Leaf) {

        Write-Info "package-lock.json was found."
        Write-Info "Checking whether the existing dependency tree matches the lockfile."


        $DryRunExitCode = 1
        $OriginalLocation = (Get-Location).Path

        try {
            Set-Location $FrontendRoot

            Write-CommandHeader "npm ci --dry-run"

            & npm ci --dry-run --ignore-scripts

            $DryRunExitCode = [int]$LASTEXITCODE
        }
        catch {
            Write-Info "Unable to perform npm dependency validation."
            Write-Info $_.Exception.Message

            $DryRunExitCode = 1
        }
        finally {
            Set-Location $OriginalLocation
        }

        Write-CommandFooter -ExitCode $DryRunExitCode


        if ($DryRunExitCode -eq 0) {
            Write-Success "Existing npm dependencies are compatible with package-lock.json."
            Write-Info "Existing dependencies will be reused."

            return $true
        }


        Write-Info "Existing dependencies do not match the current package-lock.json."
        Write-Info "The dependency tree will be refreshed."

        return $false
    }


    # --------------------------------------------------------
    # No package-lock.json
    # --------------------------------------------------------

    Write-Info "No package-lock.json was found."
    Write-Info "Dependency state cannot be validated against a lockfile."
    Write-Info "npm install will be used to resolve the required packages."

    return $false
}


# ============================================================
# Install-FrontendDependency
# ============================================================
#
# Installs or refreshes frontend npm dependencies.
#
# Behaviour:
#
# 1. Existing valid dependencies:
#       Reuse them.
#
# 2. Missing dependencies + package-lock.json:
#       npm ci
#
# 3. Missing dependencies + no lockfile:
#       npm install
#
# 4. Existing but outdated/inconsistent dependencies:
#       npm ci when lockfile exists
#
# 5. Existing dependencies without lockfile:
#       npm install
#
# ============================================================

function Install-FrontendDependency {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Dependencies"


    # --------------------------------------------------------
    # Verify package.json
    # --------------------------------------------------------

    Write-Step "Checking frontend project files."

    if (-not (Test-Path $FrontendPackageFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The frontend package.json file was not found: $FrontendPackageFile" `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Found package.json."


    # --------------------------------------------------------
    # Verify npm
    # --------------------------------------------------------

    if (-not (Test-CommandExistence "npm")) {
        Write-SetupFailure `
            -Message "npm was not found. Node.js must be installed before frontend dependencies can be installed." `
            -ExitCode $EXIT_NODE
    }

    Write-Success "npm is available."


    # --------------------------------------------------------
    # Determine dependency state
    # --------------------------------------------------------

    $DependenciesValid = Test-NpmDependencies


    if ($DependenciesValid) {

        Write-Success "SmartFit frontend dependencies are already available."
        Write-Info "Skipping dependency download."
        Write-Info "Existing node_modules will be used."

        return
    }


    # --------------------------------------------------------
    # Dependency installation required
    # --------------------------------------------------------

    $NpmExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Frontend dependencies require installation or refresh."


    try {
        Set-Location $FrontendRoot


        # ----------------------------------------------------
        # package-lock.json available
        # ----------------------------------------------------

        if (Test-Path $FrontendLockFile -PathType Leaf) {

            Write-Info "package-lock.json detected."
            Write-Info "Using npm ci for a clean, reproducible dependency installation."
            Write-Info "npm ci installs the exact dependency versions recorded in the lockfile."

            Write-CommandHeader "npm ci"

            & npm ci

            $NpmExitCode = [int]$LASTEXITCODE
        }


        # ----------------------------------------------------
        # No package-lock.json
        # ----------------------------------------------------

        else {

            Write-Info "package-lock.json was not found."
            Write-Info "Using npm install to resolve frontend dependencies."

            Write-CommandHeader "npm install"

            & npm install

            $NpmExitCode = [int]$LASTEXITCODE
        }
    }
    catch {
        Write-Info "An exception occurred while installing frontend dependencies."
        Write-Info $_.Exception.Message

        $NpmExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }


    Write-CommandFooter -ExitCode $NpmExitCode


    # --------------------------------------------------------
    # Verify installation
    # --------------------------------------------------------

    if ($NpmExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Frontend npm dependency installation failed." `
            -ExitCode $EXIT_FRONTEND
    }


    if (-not (Test-Path $FrontendNodeModules -PathType Container)) {
        Write-SetupFailure `
            -Message "npm completed successfully, but the node_modules directory was not found afterwards." `
            -ExitCode $EXIT_FRONTEND
    }


    Write-Success "Frontend npm dependencies are ready."
    Write-Info "Dependencies location: $FrontendNodeModules"
}


# ============================================================
# Invoke-FrontendBuild
# ============================================================
#
# Builds the React/Vite frontend.
#
# npm run build uses the build script defined in package.json.
#
# ============================================================

function Invoke-FrontendBuild {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Build"


    # --------------------------------------------------------
    # Verify package.json
    # --------------------------------------------------------

    Write-Step "Checking frontend build configuration."

    if (-not (Test-Path $FrontendPackageFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The frontend package.json file was not found: $FrontendPackageFile" `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Found package.json."


    # --------------------------------------------------------
    # Verify dependencies
    # --------------------------------------------------------

    if (-not (Test-Path $FrontendNodeModules -PathType Container)) {
        Write-SetupFailure `
            -Message "Frontend dependencies are not installed. The node_modules directory was not found." `
            -ExitCode $EXIT_FRONTEND
    }

    Write-Success "Frontend dependencies are available."


    # --------------------------------------------------------
    # Build frontend
    # --------------------------------------------------------

    $BuildExitCode = 1
    $OriginalLocation = (Get-Location).Path

    Write-Step "Building the SmartFit React/Vite frontend."

    Write-Info "Project directory:"
    Write-Info "  $FrontendRoot"

    Write-Info "Build command:"
    Write-Info "  npm run build"


    try {
        Set-Location $FrontendRoot

        Write-CommandHeader "npm run build"

        & npm run build

        $BuildExitCode = [int]$LASTEXITCODE
    }
    catch {
        Write-Info "An exception occurred during the frontend build."
        Write-Info $_.Exception.Message

        $BuildExitCode = 1
    }
    finally {
        Set-Location $OriginalLocation
    }


    Write-CommandFooter -ExitCode $BuildExitCode


    # --------------------------------------------------------
    # Verify build result
    # --------------------------------------------------------

    if ($BuildExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Frontend build failed." `
            -ExitCode $EXIT_FRONTEND
    }


    if (-not (Test-Path $FrontendDist -PathType Container)) {
        Write-SetupFailure `
            -Message "The frontend build command succeeded, but the expected dist directory was not created." `
            -ExitCode $EXIT_FRONTEND
    }


    Write-Success "SmartFit frontend build completed successfully."
    Write-Info "Production build directory:"
    Write-Info "  $FrontendDist"
}


# ============================================================
# Initialize-Frontend
# ============================================================
#
# Main entry point for the frontend installation process.
#
# ============================================================

function Initialize-Frontend {
    [CmdletBinding()]
    param ()

    Write-Section "Frontend Setup"

    Write-Step "Starting SmartFit frontend environment preparation."

    Write-Info "Frontend root:"
    Write-Info "  $FrontendRoot"

    Write-Info "Package file:"
    Write-Info "  $FrontendPackageFile"

    Write-Info "Dependencies directory:"
    Write-Info "  $FrontendNodeModules"

    Write-Info "Build output:"
    Write-Info "  $FrontendDist"


    # ========================================================
    # STEP 1 - Detect Node.js and npm
    # ========================================================

    Write-Section "Runtime Verification"

    $DetectedNode = Find-Node
    $DetectedNpm = Find-Npm


    # --------------------------------------------------------
    # Node.js/npm missing
    # --------------------------------------------------------

    if (-not $DetectedNode -or -not $DetectedNpm) {

        Write-Info "Node.js and/or npm is missing."
        Write-Info "Starting automatic Node.js LTS installation."

        Install-Node
    }


    # --------------------------------------------------------
    # Node.js/npm already available
    # --------------------------------------------------------

    else {

        Write-Success "Node.js and npm are already available."
        Write-Info "No Node.js installation is required."
    }


    # ========================================================
    # STEP 2 - Refresh PATH
    # ========================================================

    Write-Step "Refreshing the current process PATH."

    Initialize-ProcessPath


    # ========================================================
    # STEP 3 - Final runtime verification
    # ========================================================

    Write-Step "Performing final Node.js/npm verification."

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

    Write-Success "Node.js and npm are ready."


    # Display final runtime versions for diagnostics.

    Write-Info "Final Node.js version:"
    & node --version

    Write-Info "Final npm version:"
    & npm --version


    # ========================================================
    # STEP 4 - Install/reuse dependencies
    # ========================================================

    Install-FrontendDependency


    # ========================================================
    # STEP 5 - Build frontend
    # ========================================================

    Invoke-FrontendBuild


    # ========================================================
    # COMPLETE
    # ========================================================

    Write-Section "Frontend Setup Complete"

    Write-Success "SmartFit frontend setup completed successfully."

    Write-Info "Node.js: available"
    Write-Info "npm: available"
    Write-Info "Frontend dependencies: ready"
    Write-Info "Frontend build: successful"

    Write-Info "Production files are available in:"
    Write-Info "  $FrontendDist"
}
