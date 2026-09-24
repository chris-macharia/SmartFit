# ============================================================
# SmartFit v0.0.1
# Windows Installer - Python Environment Module
# ============================================================

$PythonWingetId = "Python.Python"

$BackendRoot = Join-Path $ProjectRoot "backend"
$VenvPath = Join-Path $BackendRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$RequirementsFile = Join-Path $BackendRoot "requirements.txt"

$EXIT_PYTHON = 20
$EXIT_WINGET = 21
$EXIT_BACKEND_SETUP = 50

$script:PythonCommand = $null


# ============================================================
# FIND PYTHON
# ============================================================

function Find-Python {

    Write-Step "Checking for an installed Python interpreter."

    $Candidates = @(
        "python",
        "py"
    )

    foreach ($Candidate in $Candidates) {

        $Command = Get-Command $Candidate -ErrorAction SilentlyContinue

        if ($null -eq $Command) {
            continue
        }

        try {

            $VersionOutput = & $Candidate --version 2>&1
            $CommandExitCode = [int]$LASTEXITCODE

            if ($CommandExitCode -ne 0) {
                continue
            }

            Write-Info "Detected Python command: $Candidate"
            Write-Info "Python version: $VersionOutput"

            return $Candidate
        }
        catch {
            continue
        }
    }

    Write-Info "No working Python interpreter was detected."

    return $null
}


# ============================================================
# INSTALL PYTHON
# ============================================================

function Install-Python {

    Write-Step "Python was not found. Preparing automatic installation."

    if (-not (Test-CommandExistence "winget")) {

        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install Python automatically." `
            -ExitCode $EXIT_WINGET
    }

    Write-Info "Installing Python using winget."

    Write-CommandHeader "winget install --id $PythonWingetId --exact --source winget"

    & winget install `
        --id $PythonWingetId `
        --exact `
        --source winget

    $WingetExitCode = [int]$LASTEXITCODE

    Write-CommandFooter -ExitCode $WingetExitCode

    if ($WingetExitCode -ne 0) {

        Write-SetupFailure `
            -Message "Python installation failed through winget." `
            -ExitCode $EXIT_PYTHON
    }

    Initialize-ProcessPath

    $DetectedPython = Find-Python

    if ($null -eq $DetectedPython) {

        Write-SetupFailure `
            -Message "Python was installed, but no working Python interpreter could be detected afterwards." `
            -ExitCode $EXIT_PYTHON
    }

    Write-Success "Python installation completed."

    return $DetectedPython
}


# ============================================================
# INITIALIZE PYTHON
# ============================================================

function Initialize-Python {

    Write-Section "Python Environment"

    $DetectedPython = Find-Python

    if ($null -eq $DetectedPython) {
        $DetectedPython = Install-Python
    }

    $script:PythonCommand = $DetectedPython

    if (-not (Test-Path $RequirementsFile -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend requirements.txt file was not found: $RequirementsFile" `
            -ExitCode $EXIT_BACKEND_SETUP
    }


    if (-not (Test-Path $VenvPython -PathType Leaf)) {

        Write-Step "Creating the SmartFit Python virtual environment."

        Push-Location $BackendRoot

        try {

            Write-CommandHeader "$DetectedPython -m venv .venv"

            & $DetectedPython -m venv ".venv"

            $VenvExitCode = [int]$LASTEXITCODE

            Write-CommandFooter -ExitCode $VenvExitCode

            if ($VenvExitCode -ne 0) {

                Write-SetupFailure `
                    -Message "Python virtual environment creation failed." `
                    -ExitCode $EXIT_BACKEND_SETUP
            }
        }
        finally {
            Pop-Location
        }
    }
    else {

        Write-Info "Existing Python virtual environment detected."
    }


    if (-not (Test-Path $VenvPython -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The Python virtual environment was not created correctly: $VenvPython" `
            -ExitCode $EXIT_BACKEND_SETUP
    }

    Write-Success "Python virtual environment is ready."


    Push-Location $BackendRoot

    try {

        Write-Step "Upgrading pip inside the SmartFit virtual environment."

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pip install --upgrade pip"

        & $VenvPython -m pip install --upgrade pip

        $PipExitCode = [int]$LASTEXITCODE

        Write-CommandFooter -ExitCode $PipExitCode

        if ($PipExitCode -ne 0) {

            Write-SetupFailure `
                -Message "pip upgrade failed." `
                -ExitCode $EXIT_BACKEND_SETUP
        }


        Write-Step "Installing SmartFit backend Python dependencies."

        Write-CommandHeader ".\.venv\Scripts\python.exe -m pip install -r requirements.txt"

        & $VenvPython -m pip install -r $RequirementsFile

        $RequirementsExitCode = [int]$LASTEXITCODE

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


    Write-Success "Python backend environment is ready."
}