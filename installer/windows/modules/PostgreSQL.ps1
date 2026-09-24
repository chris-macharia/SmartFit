# ============================================================
# SmartFit v0.0.1
# PostgreSQL Installer
# ============================================================
#
# This module:
# 1. Detects PostgreSQL.
# 2. Installs PostgreSQL 18 using winget when required.
# 3. Preserves an existing PostgreSQL password.
# 4. Uses SmartFit2026 for a new PostgreSQL installation.
# 5. Verifies PostgreSQL authentication.
# 6. Creates SmartFit_db and SmartFit_Test_db when missing.
# 7. Updates the backend .env database configuration.
#
# IMPORTANT:
# The existing backend .env file is preserved.
# Only PostgreSQL-related configuration values are changed.
#
# Database configuration written by this installer:
#
# DATABASE_URL=postgresql://postgres:SmartFit2026@localhost:5432/SmartFit_db
# TEST_DATABASE_URL=postgresql://postgres:SmartFit2026@localhost:5432/SmartFit_Test_db
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=SmartFit2026
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=SmartFit_db
#
# Exit codes:
# 30 - PostgreSQL installation failure
# 31 - PostgreSQL authentication/connection failure
# 32 - Database creation failure
# 40 - Environment configuration failure
# ============================================================

$PostgresWingetId = "PostgreSQL.PostgreSQL.18"
$PostgresUser = "postgres"
$DefaultPostgresPassword = "SmartFit2026"

$PostgresHost = "localhost"
$PostgresPort = "5432"

$DevelopmentDatabase = "SmartFit_db"
$TestDatabase = "SmartFit_Test_db"

$PostgresBinDirectory = "C:\Program Files\PostgreSQL\18\bin"

$BackendRoot = Join-Path $ProjectRoot "backend"
$BackendEnvFile = Join-Path $BackendRoot ".env"

$EXIT_POSTGRES_INSTALL = 30
$EXIT_POSTGRES_AUTH = 31
$EXIT_DATABASE = 32
$EXIT_ENV = 40

$script:PsqlPath = $null
$script:PostgresPassword = $null
$script:PostgresWasPreviouslyInstalled = $false


# ============================================================
# Find PostgreSQL psql
# ============================================================

function Find-Psql {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    $Command = Get-Command "psql" -ErrorAction SilentlyContinue

    if ($Command) {
        return $Command.Source
    }

    $CandidatePaths = @(
        (Join-Path $PostgresBinDirectory "psql.exe"),
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe",
        "C:\Program Files\PostgreSQL\14\bin\psql.exe"
    )

    foreach ($CandidatePath in $CandidatePaths) {
        if (Test-Path $CandidatePath -PathType Leaf) {
            return $CandidatePath
        }
    }

    return $null
}


# ============================================================
# Detect PostgreSQL installation
# ============================================================

function Find-PostgreSQL {
    [CmdletBinding()]
    [OutputType([bool])]
    param ()

    $PsqlCommand = Find-Psql

    if ($PsqlCommand) {
        $script:PsqlPath = $PsqlCommand
        return $true
    }

    $Service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue |
        Select-Object -First 1

    if ($Service) {
        $PsqlCommand = Find-Psql

        if ($PsqlCommand) {
            $script:PsqlPath = $PsqlCommand
            return $true
        }
    }

    return $false
}


# ============================================================
# Install PostgreSQL
# ============================================================

function Install-PostgreSQL {
    [CmdletBinding()]
    param ()

    Write-Section "PostgreSQL Installation"

    if (-not (Test-CommandExistence "winget")) {
        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install PostgreSQL automatically." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }

    $WingetExitCode = 1

    Write-Step "Installing PostgreSQL 18 using winget."
    Write-CommandHeader "winget install --id $PostgresWingetId --exact --source winget"

    try {
        & winget install `
            --id $PostgresWingetId `
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
            -Message "PostgreSQL installation failed through winget." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }

    Initialize-ProcessPath

    if (-not (Find-PostgreSQL)) {
        Write-SetupFailure `
            -Message "PostgreSQL was installed, but psql could not be detected." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }

    $script:PostgresWasPreviouslyInstalled = $false
    $script:PostgresPassword = $DefaultPostgresPassword

    Write-Success "PostgreSQL is installed."
    Write-Info "The SmartFit PostgreSQL password is: $DefaultPostgresPassword"
}


# ============================================================
# Request password for existing PostgreSQL installation
# ============================================================

function Request-ExistingPostgresPassword {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    Write-Step "PostgreSQL is already installed."

    Write-Info "The existing PostgreSQL password will not be changed."
    Write-Info "Enter the current password for the PostgreSQL postgres user."

    $EnteredCredential = Read-Host "PostgreSQL password"

    if ([string]::IsNullOrWhiteSpace($EnteredCredential)) {
        Write-SetupFailure `
            -Message "A PostgreSQL password is required to continue." `
            -ExitCode $EXIT_POSTGRES_AUTH
    }

    return $EnteredCredential
}


# ============================================================
# Test PostgreSQL authentication
# ============================================================

function Test-PostgresAuthentication {
    [CmdletBinding()]
    [OutputType([bool])]
    param ()

    if (-not $script:PsqlPath) {
        $script:PsqlPath = Find-Psql
    }

    if (-not $script:PsqlPath) {
        return $false
    }

    $PreviousPgPassword = $env:PGPASSWORD

    try {
        $env:PGPASSWORD = $script:PostgresPassword

        & $script:PsqlPath `
            --host=$PostgresHost `
            --port=$PostgresPort `
            --username=$PostgresUser `
            --dbname=postgres `
            --command="SELECT 1;" `
            --no-password `
            2>&1 | Out-Null

        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
    finally {
        $env:PGPASSWORD = $PreviousPgPassword
    }
}


# ============================================================
# Create PostgreSQL database when missing
# ============================================================

function New-DatabaseIfMissing {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param (
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )

    if (-not $script:PsqlPath) {
        $script:PsqlPath = Find-Psql
    }

    if (-not $script:PsqlPath) {
        Write-SetupFailure `
            -Message "psql could not be found." `
            -ExitCode $EXIT_DATABASE
    }

    $DatabaseCheckOutput = $null
    $DatabaseCheckExitCode = 1

    $PreviousPgPassword = $env:PGPASSWORD

    try {
        $env:PGPASSWORD = $script:PostgresPassword

        $DatabaseCheckOutput = & $script:PsqlPath `
            --host=$PostgresHost `
            --port=$PostgresPort `
            --username=$PostgresUser `
            --dbname=postgres `
            --command="SELECT 1 FROM pg_database WHERE datname='$DatabaseName';" `
            --tuples-only `
            --no-align `
            --no-password `
            2>&1

        $DatabaseCheckExitCode = [int]$LASTEXITCODE
    }
    catch {
        $DatabaseCheckExitCode = 1
    }
    finally {
        $env:PGPASSWORD = $PreviousPgPassword
    }

    if ($DatabaseCheckExitCode -ne 0) {
        Write-SetupFailure `
            -Message "Unable to check whether database '$DatabaseName' exists." `
            -ExitCode $EXIT_DATABASE
    }

    if ($DatabaseCheckOutput -match "1") {
        Write-Info "Database already exists: $DatabaseName"
        return
    }

    if ($PSCmdlet.ShouldProcess($DatabaseName, "Create PostgreSQL database")) {
        $CreateExitCode = 1
        $PreviousPgPassword = $env:PGPASSWORD

        try {
            $env:PGPASSWORD = $script:PostgresPassword

            Write-CommandHeader "CREATE DATABASE $DatabaseName"

            & $script:PsqlPath `
                --host=$PostgresHost `
                --port=$PostgresPort `
                --username=$PostgresUser `
                --dbname=postgres `
                --command="CREATE DATABASE `"$DatabaseName`";" `
                --no-password

            $CreateExitCode = [int]$LASTEXITCODE
        }
        catch {
            $CreateExitCode = 1
        }
        finally {
            $env:PGPASSWORD = $PreviousPgPassword
        }

        Write-CommandFooter -ExitCode $CreateExitCode

        if ($CreateExitCode -ne 0) {
            Write-SetupFailure `
                -Message "Failed to create PostgreSQL database '$DatabaseName'." `
                -ExitCode $EXIT_DATABASE
        }

        Write-Success "Database created: $DatabaseName"
    }
}


# ============================================================
# Update one environment variable in the .env file
# ============================================================

function Write-EnvValue {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$Key,

        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    $NewLine = "$Key=$Value"

    $Pattern = "^\s*$([regex]::Escape($Key))\s*=.*$"

    if ($Content -match $Pattern) {
        return [regex]::Replace(
            $Content,
            $Pattern,
            $NewLine,
            [System.Text.RegularExpressions.RegexOptions]::Multiline
        )
    }

    if ([string]::IsNullOrWhiteSpace($Content)) {
        return $NewLine
    }

    return "$Content`r`n$NewLine"
}


# ============================================================
# Update backend .env database configuration
# ============================================================

function Write-PostgresEnvironment {
    [CmdletBinding()]
    param ()

    Write-Section "Backend Database Environment"

    if (-not (Test-Path $BackendRoot -PathType Container)) {
        Write-SetupFailure `
            -Message "The backend directory was not found: $BackendRoot" `
            -ExitCode $EXIT_ENV
    }

    try {
        # ----------------------------------------------------
        # Read existing .env if it exists.
        # ----------------------------------------------------

        if (Test-Path $BackendEnvFile -PathType Leaf) {
            $EnvironmentContent = Get-Content `
                -Path $BackendEnvFile `
                -Raw `
                -ErrorAction Stop

            Write-Info "Existing backend .env file found."
            Write-Info "Existing non-database configuration will be preserved."
        }
        else {
            $EnvironmentContent = ""

            Write-Info "No backend .env file was found."
            Write-Info "A new backend .env file will be created."
        }

        # ----------------------------------------------------
        # URL-encode credentials for DATABASE_URL.
        # ----------------------------------------------------

        $EncodedUser = [System.Uri]::EscapeDataString(
            $PostgresUser
        )

        $EncodedPassword = [System.Uri]::EscapeDataString(
            $script:PostgresPassword
        )

        $DevelopmentDatabaseUrl = `
            "postgresql://${EncodedUser}:${EncodedPassword}@${PostgresHost}:${PostgresPort}/${DevelopmentDatabase}"

        $TestDatabaseUrl = `
            "postgresql://${EncodedUser}:${EncodedPassword}@${PostgresHost}:${PostgresPort}/${TestDatabase}"

        # ----------------------------------------------------
        # Update only PostgreSQL-related environment variables.
        # ----------------------------------------------------

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "DATABASE_URL" `
            -Value $DevelopmentDatabaseUrl

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "TEST_DATABASE_URL" `
            -Value $TestDatabaseUrl

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "POSTGRES_USER" `
            -Value $PostgresUser

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "POSTGRES_PASSWORD" `
            -Value $script:PostgresPassword

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "POSTGRES_HOST" `
            -Value $PostgresHost

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "POSTGRES_PORT" `
            -Value $PostgresPort

        $EnvironmentContent = Write-EnvValue `
            -Content $EnvironmentContent `
            -Key "POSTGRES_DB" `
            -Value $DevelopmentDatabase

        # ----------------------------------------------------
        # Write the updated .env.
        # ----------------------------------------------------

        Set-Content `
            -Path $BackendEnvFile `
            -Value $EnvironmentContent.TrimEnd() `
            -Encoding UTF8 `
            -Force `
            -ErrorAction Stop
    }
    catch {
        Write-SetupFailure `
            -Message "Failed to update the backend .env file: $($_.Exception.Message)" `
            -ExitCode $EXIT_ENV
    }

    if (-not (Test-Path $BackendEnvFile -PathType Leaf)) {
        Write-SetupFailure `
            -Message "The backend .env file was not created: $BackendEnvFile" `
            -ExitCode $EXIT_ENV
    }

    Write-Success "Backend database environment configured."
    Write-Info "Environment file: $BackendEnvFile"
    Write-Info "Development database: $DevelopmentDatabase"
    Write-Info "Test database: $TestDatabase"
}


# ============================================================
# Main PostgreSQL setup
# ============================================================

function Initialize-PostgreSQL {
    [CmdletBinding()]
    param ()

    Write-Section "PostgreSQL Setup"

    $ExistingPostgreSQL = Find-PostgreSQL

    # --------------------------------------------------------
    # Existing PostgreSQL installation
    # --------------------------------------------------------

    if ($ExistingPostgreSQL) {
        $script:PostgresWasPreviouslyInstalled = $true

        Write-Success "Existing PostgreSQL installation detected."
        Write-Info "The existing PostgreSQL password will be preserved."

        $script:PostgresPassword = Request-ExistingPostgresPassword

        Write-Step "Verifying the existing PostgreSQL credentials."

        if (-not (Test-PostgresAuthentication)) {
            Write-SetupFailure `
                -Message "The supplied PostgreSQL password could not be verified." `
                -ExitCode $EXIT_POSTGRES_AUTH
        }

        Write-Success "Existing PostgreSQL credentials verified."
    }

    # --------------------------------------------------------
    # New PostgreSQL installation
    # --------------------------------------------------------

    else {
        Install-PostgreSQL

        Write-Step "Verifying the new PostgreSQL installation."

        if (-not (Test-PostgresAuthentication)) {
            Write-SetupFailure `
                -Message "The default PostgreSQL password could not be verified after installation." `
                -ExitCode $EXIT_POSTGRES_AUTH
        }

        Write-Success "New PostgreSQL credentials verified."
    }

    # --------------------------------------------------------
    # Refresh PATH and verify PostgreSQL
    # --------------------------------------------------------

    Initialize-ProcessPath

    if (-not (Find-PostgreSQL)) {
        Write-SetupFailure `
            -Message "PostgreSQL could not be located after setup." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }

    # --------------------------------------------------------
    # Create SmartFit databases
    # --------------------------------------------------------

    New-DatabaseIfMissing `
        -DatabaseName $DevelopmentDatabase

    New-DatabaseIfMissing `
        -DatabaseName $TestDatabase

    # --------------------------------------------------------
    # Update backend environment
    # --------------------------------------------------------

    Write-PostgresEnvironment

    # --------------------------------------------------------
    # Completion information
    # --------------------------------------------------------

    Write-Success "PostgreSQL setup completed successfully."

    if (-not $script:PostgresWasPreviouslyInstalled) {
        Write-Info "Development PostgreSQL password: $($script:PostgresPassword)"
        Write-Info "Change this password after completing the development setup."
        Write-Info "If the password is changed in pgAdmin, update the backend .env file as well."
    }
    else {
        Write-Info "Existing PostgreSQL password was preserved."
        Write-Info "The backend .env file uses the verified existing password."
    }
}