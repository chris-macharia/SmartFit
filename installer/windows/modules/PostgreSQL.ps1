# ============================================================
# SmartFit v0.0.1
# Windows Installer - PostgreSQL Module
# ============================================================
#
# This module:
#
# 1. Detects PostgreSQL.
# 2. Installs PostgreSQL 18 using winget when required.
# 3. Preserves an existing PostgreSQL password.
# 4. Uses SmartFit2026 for a new PostgreSQL installation.
# 5. Verifies PostgreSQL authentication.
# 6. Creates SmartFit_db when missing.
# 7. Creates SmartFit_Test_db when missing.
# 8. Preserves existing backend .env configuration.
# 9. Updates only PostgreSQL-related .env values.
# 10. Synchronizes database configuration into the current
#     PowerShell process environment.
# 11. Verifies the generated database configuration.
#
# IMPORTANT:
#
# The existing backend .env file is preserved.
# Only PostgreSQL-related configuration values are changed.
#
# Database configuration written by this installer:
#
# DATABASE_URL=postgresql://postgres:<encoded-password>@localhost:5432/SmartFit_db
# TEST_DATABASE_URL=postgresql://postgres:<encoded-password>@localhost:5432/SmartFit_Test_db
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=<password>
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=SmartFit_db
#
# The password is URL-encoded inside DATABASE_URL and
# TEST_DATABASE_URL so that special characters in the PostgreSQL
# password cannot produce an invalid SQLAlchemy URL.
#
# Exit codes:
# 30 - PostgreSQL installation failure
# 31 - PostgreSQL authentication/connection failure
# 32 - Database creation failure
# 40 - Environment configuration failure
# ============================================================


# ============================================================
# PostgreSQL Configuration
# ============================================================

$PostgresWingetId = "PostgreSQL.PostgreSQL.18"

$PostgresUser = "postgres"

# Password used only when PostgreSQL is installed by this installer.
#
# If PostgreSQL already exists, the installer asks for the existing
# password and does NOT replace it.
$DefaultPostgresPassword = "SmartFit2026"

$PostgresHost = "localhost"
$PostgresPort = "5432"

$DevelopmentDatabase = "SmartFit_db"
$TestDatabase = "SmartFit_Test_db"

# Default PostgreSQL 18 installation location.
$PostgresBinDirectory = "C:\Program Files\PostgreSQL\18\bin"


# ============================================================
# SmartFit Paths
# ============================================================

$BackendRoot = Join-Path $ProjectRoot "backend"

$BackendEnvFile = Join-Path `
    $BackendRoot `
    ".env"


# ============================================================
# Exit Codes
# ============================================================

$EXIT_POSTGRES_INSTALL = 30
$EXIT_POSTGRES_AUTH = 31
$EXIT_DATABASE = 32
$EXIT_ENV = 40


# ============================================================
# Module State
# ============================================================

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

    # --------------------------------------------------------
    # First check whether psql is already available on PATH.
    # --------------------------------------------------------

    $Command = Get-Command `
        "psql" `
        -ErrorAction SilentlyContinue

    if ($Command) {
        return $Command.Source
    }


    # --------------------------------------------------------
    # Check common PostgreSQL installation locations.
    #
    # PostgreSQL 18 is the expected SmartFit installation.
    # Older versions are also checked so that an existing
    # PostgreSQL installation can be reused.
    # --------------------------------------------------------

    $CandidatePaths = @(
        (Join-Path $PostgresBinDirectory "psql.exe"),
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe",
        "C:\Program Files\PostgreSQL\14\bin\psql.exe"
    )


    foreach ($CandidatePath in $CandidatePaths) {

        if (Test-Path `
            $CandidatePath `
            -PathType Leaf) {

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


    # --------------------------------------------------------
    # As an additional check, look for a PostgreSQL service.
    # --------------------------------------------------------

    $Service = Get-Service `
        -Name "postgresql*" `
        -ErrorAction SilentlyContinue |
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


    # --------------------------------------------------------
    # Verify winget.
    # --------------------------------------------------------

    if (-not (Test-CommandExistence "winget")) {

        Write-SetupFailure `
            -Message "Windows Package Manager (winget) is required to install PostgreSQL automatically." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }


    $WingetExitCode = 1


    Write-Step "Installing PostgreSQL 18 using winget."


    Write-CommandHeader `
        "winget install --id $PostgresWingetId --exact --source winget"


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


    Write-CommandFooter `
        -ExitCode $WingetExitCode


    if ($WingetExitCode -ne 0) {

        Write-SetupFailure `
            -Message "PostgreSQL installation failed through winget." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }


    # --------------------------------------------------------
    # Refresh PATH because winget may have installed psql into
    # a directory that was not present in the current process.
    # --------------------------------------------------------

    Initialize-ProcessPath


    # --------------------------------------------------------
    # Verify that psql can now be found.
    # --------------------------------------------------------

    if (-not (Find-PostgreSQL)) {

        Write-SetupFailure `
            -Message "PostgreSQL was installed, but psql could not be detected." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }


    # --------------------------------------------------------
    # A newly installed PostgreSQL instance uses the SmartFit
    # default password.
    # --------------------------------------------------------

    $script:PostgresWasPreviouslyInstalled = $false

    $script:PostgresPassword = $DefaultPostgresPassword


    Write-Success "PostgreSQL is installed."

    Write-Info `
        "The SmartFit PostgreSQL password for this new installation is: $DefaultPostgresPassword"
}


# ============================================================
# Request password for existing PostgreSQL installation
# ============================================================

function Request-ExistingPostgresPassword {
    [CmdletBinding()]
    [OutputType([string])]
    param ()

    Write-Step "PostgreSQL is already installed."

    Write-Info `
        "The existing PostgreSQL password will not be changed."

    Write-Info `
        "Enter the current password for the PostgreSQL postgres user."


    $EnteredCredential = Read-Host `
        "PostgreSQL password"


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

        # ----------------------------------------------------
        # PGPASSWORD allows psql to authenticate without
        # prompting interactively.
        # ----------------------------------------------------

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

        # Restore the environment exactly as it was before
        # authentication testing.
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


    # --------------------------------------------------------
    # If the database exists, do not recreate it.
    # --------------------------------------------------------

    if ($DatabaseCheckOutput -match "1") {

        Write-Info `
            "Database already exists: $DatabaseName"

        return
    }


    # --------------------------------------------------------
    # Create the database.
    # --------------------------------------------------------

    if ($PSCmdlet.ShouldProcess(
        $DatabaseName,
        "Create PostgreSQL database"
    )) {

        $CreateExitCode = 1

        $PreviousPgPassword = $env:PGPASSWORD


        try {

            $env:PGPASSWORD = $script:PostgresPassword


            Write-CommandHeader `
                "CREATE DATABASE $DatabaseName"


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


        Write-CommandFooter `
            -ExitCode $CreateExitCode


        if ($CreateExitCode -ne 0) {

            Write-SetupFailure `
                -Message "Failed to create PostgreSQL database '$DatabaseName'." `
                -ExitCode $EXIT_DATABASE
        }


        Write-Success `
            "Database created: $DatabaseName"
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


    # --------------------------------------------------------
    # Remove a UTF-8 BOM if the existing .env file contains
    # one at the beginning of its content.
    #
    # This prevents an existing malformed first variable such
    # as "﻿DATABASE_URL" from surviving the update.
    # --------------------------------------------------------

    if ($Content.Length -gt 0 -and $Content[0] -eq [char]0xFEFF) {
        $Content = $Content.Substring(1)
    }


    $NewLine = "$Key=$Value"


    $Pattern = "^\s*$([regex]::Escape($Key))\s*=.*$"


    # --------------------------------------------------------
    # Replace an existing key.
    # --------------------------------------------------------

    if ($Content -match $Pattern) {

        return [regex]::Replace(
            $Content,
            $Pattern,
            $NewLine,
            [System.Text.RegularExpressions.RegexOptions]::Multiline
        )
    }


    # --------------------------------------------------------
    # Add the key when the file is empty.
    # --------------------------------------------------------

    if ([string]::IsNullOrWhiteSpace($Content)) {

        return $NewLine
    }


    # --------------------------------------------------------
    # Add the key to the end of the existing configuration.
    # --------------------------------------------------------

    return "$Content`r`n$NewLine"
}


# ============================================================
# Build database URLs
# ============================================================

function Get-PostgresDatabaseUrl {
    [CmdletBinding()]
    [OutputType([string])]
    param (
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )


    # --------------------------------------------------------
    # PostgreSQL credentials are URL-encoded because passwords
    # may contain characters that have special meaning inside
    # connection URLs.
    # --------------------------------------------------------

    $EncodedUser = [System.Uri]::EscapeDataString(
        $PostgresUser
    )


    $EncodedPassword = [System.Uri]::EscapeDataString(
        $script:PostgresPassword
    )


    return `
        "postgresql://${EncodedUser}:${EncodedPassword}@${PostgresHost}:${PostgresPort}/${DatabaseName}"
}


# ============================================================
# Update backend .env database configuration
# ============================================================

function Write-PostgresEnvironment {
    [CmdletBinding()]
    param ()

    Write-Section "Backend Database Environment"


    # --------------------------------------------------------
    # Verify backend directory.
    # --------------------------------------------------------

    if (-not (Test-Path `
        $BackendRoot `
        -PathType Container)) {

        Write-SetupFailure `
            -Message "The backend directory was not found: $BackendRoot" `
            -ExitCode $EXIT_ENV
    }


    try {

        # ----------------------------------------------------
        # Read existing .env when present.
        # ----------------------------------------------------

        if (Test-Path `
            $BackendEnvFile `
            -PathType Leaf) {

            $EnvironmentContent = Get-Content `
                -Path $BackendEnvFile `
                -Raw `
                -ErrorAction Stop


            Write-Info `
                "Existing backend .env file found."

            Write-Info `
                "Existing non-database configuration will be preserved."
        }
        else {

            $EnvironmentContent = ""


            Write-Info `
                "No backend .env file was found."

            Write-Info `
                "A new backend .env file will be created."
        }


        # ----------------------------------------------------
        # Remove an existing UTF-8 BOM before processing the
        # environment variables.
        # ----------------------------------------------------

        if (
            $EnvironmentContent.Length -gt 0 -and
            $EnvironmentContent[0] -eq [char]0xFEFF
        ) {

            $EnvironmentContent = `
                $EnvironmentContent.Substring(1)

            Write-Info `
                "Removed an existing UTF-8 BOM from backend/.env."
        }


        # ----------------------------------------------------
        # Build the database URLs.
        # ----------------------------------------------------

        $DevelopmentDatabaseUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $DevelopmentDatabase


        $TestDatabaseUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $TestDatabase


        # ----------------------------------------------------
        # Update only PostgreSQL-related variables.
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
        # Write the updated .env file as UTF-8 WITHOUT BOM.
        #
        # This is the important fix.
        #
        # Windows PowerShell's Set-Content -Encoding UTF8 can
        # write a UTF-8 BOM. That causes python-dotenv to read:
        #
        #     ﻿DATABASE_URL
        #
        # instead of:
        #
        #     DATABASE_URL
        #
        # File.WriteAllText with UTF8Encoding($false) explicitly
        # prevents the BOM.
        # ----------------------------------------------------

        $Utf8NoBom = New-Object `
            System.Text.UTF8Encoding($false)


        [System.IO.File]::WriteAllText(
            $BackendEnvFile,
            $EnvironmentContent.TrimEnd(),
            $Utf8NoBom
        )
    }
    catch {

        Write-SetupFailure `
            -Message "Failed to update the backend .env file: $($_.Exception.Message)" `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Verify that the file now exists.
    # --------------------------------------------------------

    if (-not (Test-Path `
        $BackendEnvFile `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend .env file was not created: $BackendEnvFile" `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Synchronize the database configuration into the current
    # PowerShell process environment.
    #
    # Python processes launched later by Backend.ps1 inherit
    # these values.
    #
    # This prevents an existing Windows environment variable
    # such as DATABASE_URL="" from overriding the .env value
    # when python-dotenv loads the configuration.
    # --------------------------------------------------------

    $env:DATABASE_URL = $DevelopmentDatabaseUrl

    $env:TEST_DATABASE_URL = $TestDatabaseUrl

    $env:POSTGRES_USER = $PostgresUser

    $env:POSTGRES_PASSWORD = $script:PostgresPassword

    $env:POSTGRES_HOST = $PostgresHost

    $env:POSTGRES_PORT = $PostgresPort

    $env:POSTGRES_DB = $DevelopmentDatabase


    Write-Success `
        "Backend database environment configured."


    Write-Info `
        "Environment file: $BackendEnvFile"

    Write-Info `
        "Development database: $DevelopmentDatabase"

    Write-Info `
        "Test database: $TestDatabase"

    Write-Info `
        "DATABASE_URL has been synchronized with the installer process."

    Write-Info `
        "TEST_DATABASE_URL has been synchronized with the installer process."
}


# ============================================================
# Validate backend database environment
# ============================================================

function Test-PostgresEnvironment {
    [CmdletBinding()]
    [OutputType([bool])]
    param ()


    Write-Step `
        "Verifying the backend PostgreSQL environment configuration."


    # --------------------------------------------------------
    # Verify .env exists.
    # --------------------------------------------------------

    if (-not (Test-Path `
        $BackendEnvFile `
        -PathType Leaf)) {

        Write-SetupFailure `
            -Message "The backend .env file does not exist: $BackendEnvFile" `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Build the expected URLs.
    # --------------------------------------------------------

    $ExpectedDevelopmentUrl = Get-PostgresDatabaseUrl `
        -DatabaseName $DevelopmentDatabase


    $ExpectedTestUrl = Get-PostgresDatabaseUrl `
        -DatabaseName $TestDatabase


    # --------------------------------------------------------
    # Verify the process environment.
    #
    # This is particularly important because child Python
    # processes inherit these values.
    # --------------------------------------------------------

    if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {

        Write-SetupFailure `
            -Message "DATABASE_URL is missing from the installer environment." `
            -ExitCode $EXIT_ENV
    }


    if ([string]::IsNullOrWhiteSpace($env:TEST_DATABASE_URL)) {

        Write-SetupFailure `
            -Message "TEST_DATABASE_URL is missing from the installer environment." `
            -ExitCode $EXIT_ENV
    }


    if ($env:DATABASE_URL -ne $ExpectedDevelopmentUrl) {

        Write-SetupFailure `
            -Message "DATABASE_URL does not match the SmartFit development database configuration." `
            -ExitCode $EXIT_ENV
    }


    if ($env:TEST_DATABASE_URL -ne $ExpectedTestUrl) {

        Write-SetupFailure `
            -Message "TEST_DATABASE_URL does not match the SmartFit test database configuration." `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Read the .env file.
    #
    # Do not print the password or complete URLs because they
    # contain credentials.
    # --------------------------------------------------------

    try {

        $EnvironmentContent = Get-Content `
            -Path $BackendEnvFile `
            -Raw `
            -ErrorAction Stop
    }
    catch {

        Write-SetupFailure `
            -Message "Unable to read the backend .env file: $($_.Exception.Message)" `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Verify that the .env file does NOT begin with a UTF-8 BOM.
    #
    # This specifically protects against the issue discovered
    # during SmartFit release testing.
    # --------------------------------------------------------

    if (
        $EnvironmentContent.Length -gt 0 -and
        $EnvironmentContent[0] -eq [char]0xFEFF
    ) {

        Write-SetupFailure `
            -Message "The backend .env file contains a UTF-8 BOM. DATABASE_URL may not be readable by python-dotenv." `
            -ExitCode $EXIT_ENV
    }


    # --------------------------------------------------------
    # Verify required database keys exist in .env.
    # --------------------------------------------------------

    $RequiredEnvironmentKeys = @(
        "DATABASE_URL",
        "TEST_DATABASE_URL",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB"
    )


    foreach ($Key in $RequiredEnvironmentKeys) {

        $Pattern = "(?m)^\s*$([regex]::Escape($Key))\s*=\s*(.+?)\s*$"


        if ($EnvironmentContent -notmatch $Pattern) {

            Write-SetupFailure `
                -Message "Required PostgreSQL configuration '$Key' is missing from backend/.env." `
                -ExitCode $EXIT_ENV
        }
    }


    # --------------------------------------------------------
    # Verify database URL values in .env match the values that
    # were placed into the process environment.
    #
    # This prevents the installer from reporting success when
    # the file and the Python process would see different
    # database configurations.
    # --------------------------------------------------------

    $DotEnvDatabaseUrl = $null

    $DotEnvTestDatabaseUrl = $null


    $DatabaseUrlMatch = [regex]::Match(
        $EnvironmentContent,
        "(?m)^\s*DATABASE_URL\s*=\s*(.*?)\s*$"
    )


    if ($DatabaseUrlMatch.Success) {

        $DotEnvDatabaseUrl = $DatabaseUrlMatch.Groups[1].Value.Trim()
    }


    $TestDatabaseUrlMatch = [regex]::Match(
        $EnvironmentContent,
        "(?m)^\s*TEST_DATABASE_URL\s*=\s*(.*?)\s*$"
    )


    if ($TestDatabaseUrlMatch.Success) {

        $DotEnvTestDatabaseUrl = $TestDatabaseUrlMatch.Groups[1].Value.Trim()
    }


    if ($DotEnvDatabaseUrl -ne $ExpectedDevelopmentUrl) {

        Write-SetupFailure `
            -Message "The DATABASE_URL stored in backend/.env is not the expected SmartFit development database URL." `
            -ExitCode $EXIT_ENV
    }


    if ($DotEnvTestDatabaseUrl -ne $ExpectedTestUrl) {

        Write-SetupFailure `
            -Message "The TEST_DATABASE_URL stored in backend/.env is not the expected SmartFit test database URL." `
            -ExitCode $EXIT_ENV
    }


    Write-Success `
        "Backend PostgreSQL environment configuration verified."


    Write-Info `
        "Development database configuration: verified"

    Write-Info `
        "Test database configuration: verified"

    Write-Info `
        "PostgreSQL credentials: verified without displaying the password"


    return $true
}


# ============================================================
# Main PostgreSQL setup
# ============================================================

function Initialize-PostgreSQL {
    [CmdletBinding()]
    param ()


    Write-Section "PostgreSQL Setup"


    # --------------------------------------------------------
    # Detect an existing PostgreSQL installation.
    # --------------------------------------------------------

    $ExistingPostgreSQL = Find-PostgreSQL


    # ========================================================
    # Existing PostgreSQL installation
    # ========================================================

    if ($ExistingPostgreSQL) {

        $script:PostgresWasPreviouslyInstalled = $true


        Write-Success `
            "Existing PostgreSQL installation detected."


        Write-Info `
            "The existing PostgreSQL password will be preserved."


        $script:PostgresPassword = `
            Request-ExistingPostgresPassword


        Write-Step `
            "Verifying the existing PostgreSQL credentials."


        if (-not (Test-PostgresAuthentication)) {

            Write-SetupFailure `
                -Message "The supplied PostgreSQL password could not be verified." `
                -ExitCode $EXIT_POSTGRES_AUTH
        }


        Write-Success `
            "Existing PostgreSQL credentials verified."
    }


    # ========================================================
    # New PostgreSQL installation
    # ========================================================

    else {

        Install-PostgreSQL


        Write-Step `
            "Verifying the new PostgreSQL installation."


        if (-not (Test-PostgresAuthentication)) {

            Write-SetupFailure `
                -Message "The default PostgreSQL password could not be verified after installation." `
                -ExitCode $EXIT_POSTGRES_AUTH
        }


        Write-Success `
            "New PostgreSQL credentials verified."
    }


    # ========================================================
    # Refresh PATH and verify PostgreSQL
    # ========================================================

    Initialize-ProcessPath


    if (-not (Find-PostgreSQL)) {

        Write-SetupFailure `
            -Message "PostgreSQL could not be located after setup." `
            -ExitCode $EXIT_POSTGRES_INSTALL
    }


    # ========================================================
    # Create SmartFit databases
    # ========================================================

    New-DatabaseIfMissing `
        -DatabaseName $DevelopmentDatabase


    New-DatabaseIfMissing `
        -DatabaseName $TestDatabase


    # ========================================================
    # Update backend .env
    # ========================================================

    Write-PostgresEnvironment


    # ========================================================
    # Verify the configuration BEFORE returning to setup.ps1.
    #
    # This guarantees that Initialize-Backend will receive a
    # valid database configuration.
    # ========================================================

    Test-PostgresEnvironment


    # ========================================================
    # Completion information
    # ========================================================

    Write-Success `
        "PostgreSQL setup completed successfully."


    if (-not $script:PostgresWasPreviouslyInstalled) {

        Write-Info `
            "Development PostgreSQL password: $($script:PostgresPassword)"

        Write-Info `
            "Change this password after completing the development setup."

        Write-Info `
            "If the password is changed in pgAdmin, update backend/.env as well."
    }
    else {

        Write-Info `
            "Existing PostgreSQL password was preserved."

        Write-Info `
            "The backend .env file uses the verified existing password."
    }
}