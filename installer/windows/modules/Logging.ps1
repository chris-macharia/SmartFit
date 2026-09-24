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

function Write-Step {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[STEP] $Message" -InformationAction Continue
}

function Write-Info {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[INFO] $Message" -InformationAction Continue
}

function Write-Success {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Information "[SUCCESS] $Message" -InformationAction Continue
}

function Write-WarningMessage {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Warning "[WARNING] $Message"
}

function Write-Failure {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    Write-Error "[ERROR] $Message"
}

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