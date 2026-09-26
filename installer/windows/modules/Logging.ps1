# ============================================================
# SmartFit v0.0.1
# Installer Logging and Utility Functions
# ============================================================
#
# This module provides shared logging, command execution,
# environment, and failure-handling functions.
#
# IMPORTANT:
# This file does NOT determine $ProjectRoot.
#
# The root setup.ps1 defines:
#
#     $ProjectRoot = $PSScriptRoot
#
# All installer modules then use that shared project root.
# ============================================================


# ------------------------------------------------------------
# Section output
# ------------------------------------------------------------

function Write-Section {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "" -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
    Write-Information $Message -InformationAction Continue
    Write-Information "============================================================" -InformationAction Continue
}


# ------------------------------------------------------------
# Step output
# ------------------------------------------------------------

function Write-Step {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[STEP] $Message" -InformationAction Continue
}


# ------------------------------------------------------------
# Informational output
# ------------------------------------------------------------

function Write-Info {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[INFO] $Message" -InformationAction Continue
}


# ------------------------------------------------------------
# Success output
# ------------------------------------------------------------

function Write-Success {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[SUCCESS] $Message" -InformationAction Continue
}


# ------------------------------------------------------------
# Warning output
# ------------------------------------------------------------

function Write-WarningMessage {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Warning "[WARNING] $Message"
}


# ------------------------------------------------------------
# Failure output
# ------------------------------------------------------------

function Write-Failure {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Error "[ERROR] $Message"
}


# ------------------------------------------------------------
# Installer log
# ------------------------------------------------------------
#
# This is the common logging function used internally by the
# installer modules.
#
# The function deliberately writes through Write-Information
# so normal installer output remains visible in PowerShell.
#
# Level values:
#
#     INFO
#     SUCCESS
#     WARNING
#     ERROR
#     DEBUG
#
# ------------------------------------------------------------

function Write-InstallerLog {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter()]
        [ValidateSet(
            "INFO",
            "SUCCESS",
            "WARN",
            "WARNING",
            "ERROR",
            "DEBUG"
        )]
        [string]$Level = "INFO"
    )

    $DisplayLevel = if ($Level -eq "WARN") {
        "WARNING"
    }
    else {
        $Level
    }

    Write-Information `
        "[$DisplayLevel] $Message" `
        -InformationAction Continue
}


# ------------------------------------------------------------
# Command header
# ------------------------------------------------------------

function Write-CommandHeader {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    Write-Information "" -InformationAction Continue
    Write-Information "Command:" -InformationAction Continue
    Write-Information "  $Command" -InformationAction Continue
    Write-Information "" -InformationAction Continue
}


# ------------------------------------------------------------
# Command footer
# ------------------------------------------------------------

function Write-CommandFooter {
    [CmdletBinding()]
    param (
        [Parameter()]
        [int]$ExitCode = 0
    )

    Write-Information "" -InformationAction Continue
    Write-Information "------------------------------------------------------------" -InformationAction Continue
    Write-Information "Exit code: $ExitCode" -InformationAction Continue
    Write-Information "------------------------------------------------------------" -InformationAction Continue
}


# ------------------------------------------------------------
# Setup failure
# ------------------------------------------------------------

function Write-SetupFailure {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $true)]
        [int]$ExitCode
    )

    Write-Failure $Message

    Write-Information "" -InformationAction Continue
    Write-Information "SmartFit setup stopped." -InformationAction Continue
    Write-Information "Exit code: $ExitCode" -InformationAction Continue

    exit $ExitCode
}


# ------------------------------------------------------------
# Command existence
# ------------------------------------------------------------

function Test-CommandExistence {
    [CmdletBinding()]
    [OutputType([bool])]
    param (
        [Parameter(Mandatory = $true)]
        [string]$CommandName
    )

    $Command = Get-Command `
        $CommandName `
        -ErrorAction SilentlyContinue

    return ($null -ne $Command)
}


# ------------------------------------------------------------
# Refresh current PowerShell process PATH
# ------------------------------------------------------------

function Initialize-ProcessPath {
    [CmdletBinding()]
    param ()

    Write-Info "Refreshing the current PowerShell process PATH."

    $MachinePath = [Environment]::GetEnvironmentVariable(
        "Path",
        "Machine"
    )

    $UserPath = [Environment]::GetEnvironmentVariable(
        "Path",
        "User"
    )

    if ([string]::IsNullOrWhiteSpace($MachinePath)) {
        $MachinePath = ""
    }

    if ([string]::IsNullOrWhiteSpace($UserPath)) {
        $UserPath = ""
    }

    $env:Path = "$MachinePath;$UserPath"

    Write-Info "Current PowerShell process PATH refreshed."
}


# ------------------------------------------------------------
# Execute external command
# ------------------------------------------------------------
#
# Runs an external executable while:
#
# 1. Displaying the command.
# 2. Capturing its output.
# 3. Returning the process exit code.
# 4. Logging failures consistently.
#
# The function does not automatically terminate the installer.
# The calling module decides which installer exit code applies.
#
# ------------------------------------------------------------

function Invoke-InstallerCommand {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter()]
        [string[]]$ArgumentList = @(),

        [Parameter()]
        [switch]$IgnoreExitCode
    )

    $ArgumentDisplay = if ($ArgumentList.Count -gt 0) {
        $ArgumentList -join " "
    }
    else {
        ""
    }

    $CommandDisplay = if ([string]::IsNullOrWhiteSpace($ArgumentDisplay)) {
        $FilePath
    }
    else {
        "$FilePath $ArgumentDisplay"
    }

    Write-CommandHeader $CommandDisplay

    try {
        $Output = & $FilePath @ArgumentList 2>&1

        $ExitCode = $LASTEXITCODE

        if ($Output) {
            foreach ($Line in $Output) {
                Write-Information `
                    "$Line" `
                    -InformationAction Continue
            }
        }

        Write-CommandFooter $ExitCode

        if (($ExitCode -ne 0) -and (-not $IgnoreExitCode)) {
            Write-InstallerLog `
                -Message "Command failed with exit code $ExitCode." `
                -Level "ERROR"

            return $false
        }

        return $true
    }
    catch {
        Write-CommandFooter -ExitCode 1

        Write-InstallerLog `
            -Message "Failed to execute command: $($_.Exception.Message)" `
            -Level "ERROR"

        if (-not $IgnoreExitCode) {
            return $false
        }

        return $false
    }
}


# ------------------------------------------------------------
# Require external command
# ------------------------------------------------------------
#
# Verifies that an executable is available before a module
# attempts to use it.
#
# ------------------------------------------------------------

function Assert-CommandExists {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$CommandName,

        [Parameter()]
        [string]$Description = $CommandName
    )

    if (-not (Test-CommandExistence $CommandName)) {
        Write-InstallerLog `
            -Message "$Description was not found: $CommandName" `
            -Level "ERROR"

        return $false
    }

    return $true
}