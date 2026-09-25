# ============================================================
# SmartFit v0.0.1
# Windows Installer - Python Environment Module
# ============================================================
#
# This module:
# 1. Detects a compatible Python 3.12 installation.
# 2. Installs Python 3.12 using winget when required.
# 3. Creates the SmartFit virtual environment using Python 3.12.
# 4. Detects and replaces virtual environments created with
#    an incompatible Python version.
# 5. Upgrades pip inside the SmartFit virtual environment.
# 6. Installs backend Python dependencies.
# 7. Verifies the Python version used by the virtual environment.
#
# SmartFit v0.0.1 requires:
# Python 3.12.x
#
# Exit codes:
# 20 - Python installation/setup failure
# 21 - winget failure
# 50 - Backend setup failure
# ============================================================

$PythonWingetId = "Python.Python.3.12"

$RequiredPythonMajor = 3
$RequiredPythonMinor = 12

$BackendRoot = Join-Path $ProjectRoot "backend"
$VenvPath = Join-Path $BackendRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$RequirementsFile = Join-Path $BackendRoot "requirements.txt"

$EXIT_PYTHON = 20
$EXIT_WINGET = 21
$EXIT_BACKEND_SETUP = 50

$script:PythonCommand = $null


# ============================================================
# TEST PYTHON VERSION
# ============================================================

function Test-Python312 {

    [CmdletBinding()]
    [OutputType([bool])]
    param (
        [Parameter(Mandatory = $true)]
        [string]$PythonCommand
    )

    try {

        $VersionOutput = & $PythonCommand --version 2>&1
        $CommandExitCode = [int]$LASTEXITCODE

        if ($CommandExitCode -ne 0) {
            return $false
        }

        $VersionText = [string]$VersionOutput

        if ($VersionText -match "Python\s+(\d+)\.(\d+)\.(\d+)") {

            $Major = [int]$Matches[1]
            $Minor = [int]$Matches[2]

            if (
                $Major -eq $RequiredPythonMajor -and
                $Minor -eq $RequiredPythonMinor
            ) {
                return $true
            }
        }
    }
    catch {
        return $false
    }

    return $false
}


# ============================================================
# FIND PYTHON 3.12
# ============================================================

function Find-Python {

    [CmdletBinding()]
    [OutputType([string])]
    param ()

    Write-Step "Checking for a compatible Python 3.12 interpreter."

    # --------------------------------------------------------
    # First try the Python Launcher.
    #
    # "py -3.12" specifically requests Python 3.12 and avoids
    # accidentally selecting Python 3.14 or another version.
    # --------------------------------------------------------

    $PyCommand = Get-Command "py" -ErrorAction SilentlyContinue

    if ($null -ne $PyCommand) {

        try {

            $PyVersionOutput = & py -3.12 --version 2>&1
            $PyExitCode = [int]$LASTEXITCODE

            if ($PyExitCode -eq 0) {

                Write-Info "Detected Python 3.12 through the Windows Python Launcher."
                Write-Info "Python version: $PyVersionOutput"

                return "py -3.12"
            }
        }
        catch {
            # Continue checking other Python 3.12 locations.
        }
    }


    # --------------------------------------------------------
    # Check the regular "python" command.
    #
    # This is only accepted if it is actually Python 3.12.
    # --------------------------------------------------------

    $PythonCommand = Get-Command "python" -ErrorAction SilentlyContinue

    if ($null -ne $PythonCommand) {

        if (Test-Python312 -PythonCommand "python") {

            try {
                $VersionOutput = & python --version 2>&1
                Write-Info "Detected compatible Python command: python"
                Write-Info "Python version: $VersionOutput"
            }
            catch {
                Write-Info "Detected compatible Python command: python"
            }

            return "python"
        }

        try {
            $VersionOutput = & python --version 2>&1
            Write-Info "Ignoring incompatible Python interpreter: $VersionOutput"
        }
        catch {
            Write-Info "Ignoring an incompatible Python interpreter."
        }
    }


    # --------------------------------------------------------
    # Check common Python 3.12 installation locations.
    #
    # This is useful when Python 3.12 is installed but the
    # current PowerShell PATH has not been refreshed correctly.
    # --------------------------------------------------------

    $LocalPythonCandidates = @(
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "C:\Python312\python.exe"
    )

    foreach ($CandidatePath in $LocalPythonCandidates) {

        if (-not (Test-Path $CandidatePath -PathType Leaf)) {
            continue
        }

        if (Test-Python312 -PythonCommand $CandidatePath) {

            try {
                $VersionOutput = & $CandidatePath --version 2>&1

                Write-Info "Detected compatible Python installation."
                Write-Info "Python executable: $CandidatePath"
                Write-Info "Python version: $VersionOutput"
            }
            catch {
                Write-Info "Detected compatible Python installation: $CandidatePath"
            }

            return $CandidatePath
        }
    }


    Write-Info "Python 3.12 was not detected."

    return $null
}


# ============================================================
# INSTALL PYTHON 3.12
# ============================================================

function Install-Python {

    [CmdletBinding()]
    param ()

    Write-Section "Python 3.12 Installation"

    Write-Step "Python 3.12 was not found. Preparing automatic installation."

    if (-not (Test-CommandExistence "winget")) {

        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install Python 3.12 automatically." `
            -ExitCode $EXIT_WINGET
    }

    Write-Info "Installing Python 3.12 using winget."

    Write-CommandHeader "winget install --id $PythonWingetId --exact --source winget"

    $WingetExitCode = 1

    try {

        & winget install `
            --id $PythonWingetId `
            --exact `
            --source winget

        $WingetExitCode = [int]$LASTEXITCODE
    }
    catch {

        $WingetExitCode = 1
    }

    Write-CommandFooter -ExitCode $WingetExitCode

    if ($WingetExitCode -ne 0) {

        Write-SetupFailure `
            -Message "Python 3.12 installation failed through winget." `
            -ExitCode $EXIT_PYTHON
    }


    # --------------------------------------------------------
    # Refresh PATH after installation.
    # --------------------------------------------------------

    Initialize-ProcessPath


    # --------------------------------------------------------
    # Locate Python 3.12 again.
    # --------------------------------------------------------

    $DetectedPython = Find-Python

    if ($null -eq $DetectedPython) {

        Write-SetupFailure `
            -Message "Python 3.12 was installed, but a compatible Python 3.12 interpreter could not be detected afterwards." `
            -ExitCode $EXIT_PYTHON
    }

    Write-Success "Python 3.12 installation completed."

    return $DetectedPython
}


# ============================================================
# GET VIRTUAL ENVIRONMENT PYTHON VERSION
# ============================================================

function Get-VenvPythonVersion {

    [CmdletBinding()]
    [OutputType([string])]
    param ()

    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        return $null
    }

    try {

        $VersionOutput = & $VenvPython --version 2>&1
        $ExitCode = [int]$LASTEXITCODE

        if ($ExitCode -ne 0) {
            return $null
        }

        return [string]$VersionOutput
    }
    catch {

        return $null
    }
}


# ============================================================
# TEST VIRTUAL ENVIRONMENT VERSION
# ============================================================

function Test-VenvPython312 {

    [CmdletBinding()]
    [OutputType([bool])]
    param ()

    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        return $false
    }

    $VersionOutput = Get-VenvPythonVersion

    if ([string]::IsNullOrWhiteSpace($VersionOutput)) {
        return $false
    }

    if ($VersionOutput -match "Python\s+(\d+)\.(\d+)\.(\d+)") {

        $Major = [int]$Matches[1]
        $Minor = [int]$Matches[2]

        return (
            $Major -eq $RequiredPythonMajor -and
            $Minor -eq $RequiredPythonMinor
        )
    }

    return $false
}


# ============================================================
# REMOVE INCOMPATIBLE VIRTUAL ENVIRONMENT
# ============================================================

function Remove-IncompatibleVenv {

    [CmdletBinding()]
    param ()

    Write-Step "The existing SmartFit virtual environment uses an incompatible Python version."

    $ExistingVersion = Get-VenvPythonVersion

    if ([string]::IsNullOrWhiteSpace($ExistingVersion)) {

        Write-Info "The existing virtual environment could not report its Python version."
    }
    else {

        Write-Info "Existing virtual environment Python version: $ExistingVersion"
    }

    Write-Info "SmartFit v0.0.1 requires Python 3.12.x."
    Write-Info "The incompatible virtual environment will be recreated."


    # --------------------------------------------------------
    # If the current PowerShell process has the venv activated,
    # the executable may be in use. The installer itself does
    # not depend on the activated environment because it always
    # invokes the explicit backend\.venv interpreter.
    # --------------------------------------------------------

    try {

        if (Test-Path $VenvPath -PathType Container) {

            Remove-Item `
                -Path $VenvPath `
                -Recurse `
                -Force `
                -ErrorAction Stop
        }
    }
    catch {

        Write-SetupFailure `
            -Message "Unable to remove the incompatible SmartFit virtual environment. Close any terminal or process using backend\.venv and run setup again." `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    if (Test-Path $VenvPath) {

        Write-SetupFailure `
            -Message "The incompatible Python virtual environment could not be removed: $VenvPath" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    Write-Success "Incompatible Python virtual environment removed."
}


# ============================================================
# CREATE VIRTUAL ENVIRONMENT
# ============================================================

function New-SmartFitVenv {

    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$PythonCommand
    )

    Write-Step "Creating the SmartFit Python 3.12 virtual environment."

    Push-Location $BackendRoot

    try {

        Write-CommandHeader "$PythonCommand -m venv .venv"

        $VenvExitCode = 1

        try {

            if ($PythonCommand -eq "py -3.12") {

                & py -3.12 -m venv ".venv"
            }
            else {

                & $PythonCommand -m venv ".venv"
            }

            $VenvExitCode = [int]$LASTEXITCODE
        }
        catch {

            $VenvExitCode = 1
        }

        Write-CommandFooter -ExitCode $VenvExitCode

        if ($VenvExitCode -ne 0) {

            Write-SetupFailure `
                -Message "Python 3.12 virtual environment creation failed." `
                -ExitCode $EXIT_BACKEND_SETUP
        }
    }
    finally {

        Pop-Location
    }


    if (-not (Test-Path $VenvPython -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The Python virtual environment was not created correctly: $VenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    if (-not (Test-VenvPython312)) {

        $CreatedVersion = Get-VenvPythonVersion

        if ([string]::IsNullOrWhiteSpace($CreatedVersion)) {
            $CreatedVersion = "unknown"
        }

        Write-SetupFailure `
            -Message "The SmartFit virtual environment was created with an incompatible Python version: $CreatedVersion. SmartFit v0.0.1 requires Python 3.12.x." `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    $CreatedVersion = Get-VenvPythonVersion

    Write-Success "SmartFit Python 3.12 virtual environment created."
    Write-Info "Virtual environment Python version: $CreatedVersion"
}


# ============================================================
# INITIALIZE PYTHON
# ============================================================

function Initialize-Python {

    [CmdletBinding()]
    param ()

    Write-Section "Python Environment"


    # --------------------------------------------------------
    # Verify requirements file.
    # --------------------------------------------------------

    if (-not (Test-Path $RequirementsFile -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend requirements.txt file was not found: $RequirementsFile" `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    # --------------------------------------------------------
    # Locate Python 3.12 specifically.
    # --------------------------------------------------------

    $DetectedPython = Find-Python

    if ($null -eq $DetectedPython) {

        $DetectedPython = Install-Python
    }

    $script:PythonCommand = $DetectedPython


    # --------------------------------------------------------
    # Verify that the selected interpreter is actually 3.12.
    # --------------------------------------------------------

    if ($DetectedPython -eq "py -3.12") {

        $Python312Valid = $true
    }
    else {

        $Python312Valid = Test-Python312 -PythonCommand $DetectedPython
    }

    if (-not $Python312Valid) {

        Write-SetupFailure `
            -Message "The selected Python interpreter is not Python 3.12.x. SmartFit v0.0.1 requires Python 3.12.x." `
            -ExitCode $EXIT_PYTHON
    }


    # --------------------------------------------------------
    # Handle the existing virtual environment.
    # --------------------------------------------------------

    if (Test-Path $VenvPython -PathType Leaf) {

        if (Test-VenvPython312) {

            $ExistingVersion = Get-VenvPythonVersion

            Write-Success "Existing SmartFit Python 3.12 virtual environment detected."
            Write-Info "Virtual environment Python version: $ExistingVersion"
        }
        else {

            Remove-IncompatibleVenv
            New-SmartFitVenv -PythonCommand $DetectedPython
        }
    }
    else {

        New-SmartFitVenv -PythonCommand $DetectedPython
    }


    # --------------------------------------------------------
    # Final virtual environment verification.
    # --------------------------------------------------------

    if (-not (Test-Path $VenvPython -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The SmartFit Python virtual environment was not found: $VenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    if (-not (Test-VenvPython312)) {

        $VenvVersion = Get-VenvPythonVersion

        if ([string]::IsNullOrWhiteSpace($VenvVersion)) {
            $VenvVersion = "unknown"
        }

        Write-SetupFailure `
            -Message "The SmartFit virtual environment is using an unsupported Python version: $VenvVersion. Python 3.12.x is required." `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    # --------------------------------------------------------
    # Upgrade pip.
    # --------------------------------------------------------

    Push-Location $BackendRoot

    try {

        Write-Step "Upgrading pip inside the SmartFit Python 3.12 virtual environment."

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pip install --upgrade pip"

        $PipExitCode = 1

        try {

            & $VenvPython -m pip install --upgrade pip

            $PipExitCode = [int]$LASTEXITCODE
        }
        catch {

            $PipExitCode = 1
        }

        Write-CommandFooter -ExitCode $PipExitCode

        if ($PipExitCode -ne 0) {

            Write-SetupFailure `
                -Message "pip upgrade failed." `
                -ExitCode $EXIT_BACKEND_SETUP
        }


        # ----------------------------------------------------
        # Install backend dependencies.
        #
        # This is intentionally performed here because the
        # Python module owns the virtual environment and its
        # Python package installation.
        # ----------------------------------------------------

        Write-Step "Installing SmartFit backend Python dependencies."

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pip install -r requirements.txt"

        $RequirementsExitCode = 1

        try {

            & $VenvPython -m pip install -r $RequirementsFile

            $RequirementsExitCode = [int]$LASTEXITCODE
        }
        catch {

            $RequirementsExitCode = 1
        }

        Write-CommandFooter -ExitCode $RequirementsExitCode

        if ($RequirementsExitCode -ne 0) {

            Write-SetupFailure `
                -Message "Backend Python dependency installation failed." `
                -ExitCode $EXIT_BACKEND_SETUP
        }
    }
    finally {

        Pop-Location
    }


    # --------------------------------------------------------
    # Final confirmation.
    # --------------------------------------------------------

    $FinalPythonVersion = Get-VenvPythonVersion

    Write-Success "SmartFit Python backend environment is ready."
    Write-Info "Python version: $FinalPythonVersion"
    Write-Info "Virtual environment: $VenvPath"
}