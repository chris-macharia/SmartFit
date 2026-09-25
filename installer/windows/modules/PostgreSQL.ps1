# ============================================================
# SmartFit v0.0.1
# Windows Installer - PostgreSQL Module
# ============================================================
#
# This module installs and configures PostgreSQL 18 for SmartFit.
#
# Fresh installation:
#   1. Install PostgreSQL 18 through winget.
#   2. Detect the PostgreSQL installation.
#   3. Configure the postgres role password as SmartFit2026.
#   4. Verify password authentication.
#   5. Create SmartFit_db if missing.
#   6. Create SmartFit_Test_db if missing.
#   7. Preserve/update backend/.env.
#   8. Verify PostgreSQL environment configuration.
#
# Existing installation:
#   1. Detect the existing PostgreSQL installation.
#   2. Ask the user for the existing postgres password.
#   3. Verify authentication.
#   4. DO NOT change the existing password.
#   5. Create SmartFit databases if missing.
#   6. Preserve/update backend/.env.
#
# IMPORTANT:
#   - PostgreSQL passwords belong to database roles, not databases.
#   - SmartFit2026 is therefore assigned to the PostgreSQL
#     "postgres" role on a NEW installation.
#   - Existing PostgreSQL passwords are never overwritten.
#
# ============================================================

$PostgresWingetId = "PostgreSQL.PostgreSQL.18"

$PostgresUser = "postgres"

# Password used for a NEW PostgreSQL installation.
# Existing installations keep their existing password.
$DefaultPostgresPassword = "SmartFit2026"

$PostgresHost = "localhost"
$PostgresPort = "5432"

$DevelopmentDatabase = "SmartFit_db"
$TestDatabase = "SmartFit_Test_db"


$BackendRoot = Join-Path $ProjectRoot "backend"
$BackendEnvFile = Join-Path $BackendRoot ".env"

# ------------------------------------------------------------
# Exit codes
# ------------------------------------------------------------

$PostgresInstallFailureCode = 30
$PostgresAuthenticationFailureCode = 31
$PostgresDatabaseFailureCode = 32
$PostgresEnvironmentFailureCode = 40

# ------------------------------------------------------------
# Module state
# ------------------------------------------------------------

$script:PsqlPath = $null
$script:PostgresPassword = $null
$script:PostgresWasPreviouslyInstalled = $false

# ============================================================
# Find psql
# ============================================================

function Find-Psql {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Searching for PostgreSQL client (psql)..."

    # --------------------------------------------------------
    # First check PATH
    # --------------------------------------------------------

    try {

        $command = Get-Command "psql.exe" -ErrorAction SilentlyContinue

        if ($null -ne $command) {

            $resolvedPath = $command.Source

            if (Test-Path $resolvedPath) {

                Write-InstallerLog `
                    -Level "INFO" `
                    -Message "Found psql through PATH: $resolvedPath"

                return $resolvedPath
            }
        }

    }
    catch {

        Write-InstallerLog `
            -Level "DEBUG" `
            -Message "Unable to resolve psql through PATH: $($_.Exception.Message)"
    }

    # --------------------------------------------------------
    # Check known PostgreSQL installation directories
    # --------------------------------------------------------

    $candidatePaths = @(
        "C:\Program Files\PostgreSQL\18\bin\psql.exe",
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe",
        "C:\Program Files\PostgreSQL\14\bin\psql.exe"
    )

    foreach ($candidate in $candidatePaths) {

        if (Test-Path $candidate) {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "Found psql: $candidate"

            return $candidate
        }
    }

    Write-InstallerLog `
        -Level "WARN" `
        -Message "psql.exe could not be found."

    return $null
}

# ============================================================
# Find PostgreSQL
# ============================================================

function Find-PostgreSQL {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Searching for PostgreSQL installation..."

    $psql = Find-Psql

    if ($null -ne $psql) {

        $script:PsqlPath = $psql

        Write-InstallerLog `
            -Level "INFO" `
            -Message "PostgreSQL detected through psql."

        return $true
    }

    # --------------------------------------------------------
    # Check PostgreSQL Windows services
    # --------------------------------------------------------

    try {

        $services = Get-Service -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -like "postgresql*" -or
                $_.DisplayName -like "*PostgreSQL*"
            }

        if ($null -ne $services -and $services.Count -gt 0) {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "PostgreSQL Windows service detected."

            $psql = Find-Psql

            if ($null -ne $psql) {

                $script:PsqlPath = $psql

                return $true
            }
        }

    }
    catch {

        Write-InstallerLog `
            -Level "DEBUG" `
            -Message "Unable to inspect PostgreSQL services: $($_.Exception.Message)"
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL was not detected."

    return $false
}

# ============================================================
# Install PostgreSQL
# ============================================================

function Install-PostgreSQL {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Installing PostgreSQL 18..."

    # --------------------------------------------------------
    # Verify winget
    # --------------------------------------------------------

    try {

        $winget = Get-Command "winget.exe" -ErrorAction Stop

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Using winget: $($winget.Source)"
    }
    catch {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "winget is not available."

        Exit-WithInstallerCode $PostgresInstallFailureCode
    }

    # --------------------------------------------------------
    # Install PostgreSQL
    # --------------------------------------------------------

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Running PostgreSQL 18 installation..."

    & winget install `
        --id $PostgresWingetId `
        --exact `
        --source winget `
        --accept-source-agreements `
        --accept-package-agreements

    $wingetExitCode = $LASTEXITCODE

    if ($wingetExitCode -ne 0) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL installation failed. winget exit code: $wingetExitCode"

        Exit-WithInstallerCode $PostgresInstallFailureCode
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL installation command completed."

    # --------------------------------------------------------
    # Refresh PATH
    # --------------------------------------------------------

    Initialize-ProcessPath

    # --------------------------------------------------------
    # Locate PostgreSQL after installation
    # --------------------------------------------------------

    $found = $false

    for ($attempt = 1; $attempt -le 10; $attempt++) {

        Write-InstallerLog `
            -Level "DEBUG" `
            -Message "Checking PostgreSQL installation (attempt $attempt/10)..."

        if (Find-PostgreSQL) {

            $found = $true
            break
        }

        Start-Sleep -Seconds 2
    }

    if (-not $found) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL was installed but psql.exe could not be located."

        Exit-WithInstallerCode $PostgresInstallFailureCode
    }

    # --------------------------------------------------------
    # Mark installation as NEW
    # --------------------------------------------------------

    $script:PostgresWasPreviouslyInstalled = $false

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT assume that SmartFit2026 is already the PostgreSQL
    # password.
    #
    # The PostgreSQL installer initializes the cluster first.
    # We configure the postgres role password explicitly below.
    # --------------------------------------------------------

    $script:PostgresPassword = $DefaultPostgresPassword

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL 18 detected after installation."

    Write-InstallerLog `
        -Level "INFO" `
        -Message "The new PostgreSQL postgres role will be configured with the SmartFit default password."

    return $true
}

# ============================================================
# Request existing PostgreSQL password
# ============================================================

function Request-ExistingPostgresPassword {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL already exists on this machine."

    Write-Host ""
    Write-Host "PostgreSQL was detected on this machine." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "The existing PostgreSQL password will NOT be changed." -ForegroundColor Yellow
    Write-Host "Please enter the current password for the PostgreSQL '$PostgresUser' role." -ForegroundColor Yellow
    Write-Host ""

    $securePassword = Read-Host `
        -Prompt "PostgreSQL password" `
        -AsSecureString

    $credential = New-Object System.Management.Automation.PSCredential(
        $PostgresUser,
        $securePassword
    )

    $script:PostgresPassword = $credential.GetNetworkCredential().Password

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Existing PostgreSQL password was supplied by the user."

    return $true
}

# ============================================================
# Run psql command
# ============================================================

function Invoke-PostgresSql {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Sql,

        [string]$Database = "postgres",

        [switch]$SuppressOutput
    )

    if ([string]::IsNullOrWhiteSpace($script:PsqlPath)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql path has not been initialized."

        return $false
    }

    if ([string]::IsNullOrWhiteSpace($script:PostgresPassword)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL password has not been initialized."

        return $false
    }

    $previousPassword = $env:PGPASSWORD

    try {

        $env:PGPASSWORD = $script:PostgresPassword

        $arguments = @(
            "--host=$PostgresHost"
            "--port=$PostgresPort"
            "--username=$PostgresUser"
            "--dbname=$Database"
            "--no-password"
            "--command=$Sql"
        )

        if ($SuppressOutput) {

            & $script:PsqlPath @arguments 2>$null | Out-Null

        }
        else {

            & $script:PsqlPath @arguments
        }

        return ($LASTEXITCODE -eq 0)
    }
    finally {

        if ($null -eq $previousPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $previousPassword
        }
    }
}

# ============================================================
# Configure password on NEW PostgreSQL installation
# ============================================================

function Set-NewPostgresPassword {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Configuring the PostgreSQL postgres role password..."

    if ([string]::IsNullOrWhiteSpace($script:PsqlPath)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Cannot configure PostgreSQL password because psql.exe was not found."

        return $false
    }

    # --------------------------------------------------------
    # A newly initialized PostgreSQL cluster can normally be
    # accessed locally during initial configuration.
    #
    # We first attempt a local connection using the Windows
    # PostgreSQL installation's local authentication.
    #
    # No password is supplied here intentionally.
    # --------------------------------------------------------

    $previousPassword = $env:PGPASSWORD

    try {

        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Attempting local PostgreSQL administrative connection..."

        $localArguments = @(
            "--host=localhost"
            "--port=$PostgresPort"
            "--username=$PostgresUser"
            "--dbname=postgres"
            "--no-password"
            "--command=SELECT 1;"
        )

        $localOutput = & $script:PsqlPath @localArguments 2>&1

        $localExitCode = $LASTEXITCODE

        if ($localExitCode -ne 0) {

            Write-InstallerLog `
                -Level "WARN" `
                -Message "Local passwordless PostgreSQL connection was not available."

            Write-InstallerLog `
                -Level "DEBUG" `
                -Message "psql output: $localOutput"

            # ------------------------------------------------
            # Fallback:
            #
            # Some PostgreSQL Windows installations may already
            # have the desired password configured during their
            # initialization. Test SmartFit2026 before failing.
            # ------------------------------------------------

            Write-InstallerLog `
                -Level "INFO" `
                -Message "Testing the configured SmartFit default password..."

            if (Test-PostgresAuthentication -Password $DefaultPostgresPassword) {

                Write-InstallerLog `
                    -Level "INFO" `
                    -Message "PostgreSQL already accepts the SmartFit default password."

                $script:PostgresPassword = $DefaultPostgresPassword

                return $true
            }

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Unable to obtain administrative access to the newly installed PostgreSQL instance."

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "PostgreSQL may have been initialized with a password that this installer cannot determine automatically."

            return $false
        }

    }
    finally {

        if ($null -eq $previousPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $previousPassword
        }
    }

    # --------------------------------------------------------
    # We have local administrative access.
    #
    # PostgreSQL passwords are properties of roles. Therefore
    # SmartFit2026 is assigned to the postgres role.
    # --------------------------------------------------------

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Setting postgres role password to the SmartFit default password..."

    $passwordSql = @"
ALTER ROLE "$PostgresUser" WITH PASSWORD '$DefaultPostgresPassword';
"@

    $previousPassword = $env:PGPASSWORD

    try {

        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue

        & $script:PsqlPath `
            "--host=localhost" `
            "--port=$PostgresPort" `
            "--username=$PostgresUser" `
            "--dbname=postgres" `
            "--no-password" `
            "--command=$passwordSql" 2>&1 | Out-Null

        $exitCode = $LASTEXITCODE

    }
    finally {

        if ($null -eq $previousPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $previousPassword
        }
    }

    if ($exitCode -ne 0) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to configure the postgres role password."

        return $false
    }

    $script:PostgresPassword = $DefaultPostgresPassword

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL postgres role password configured successfully."

    # --------------------------------------------------------
    # Immediately verify password authentication.
    # --------------------------------------------------------

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Verifying PostgreSQL password authentication..."

    if (-not (Test-PostgresAuthentication)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL password authentication failed after password configuration."

        return $false
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL password authentication verified successfully."

    return $true
}

# ============================================================
# Test PostgreSQL authentication
# ============================================================

function Test-PostgresAuthentication {

    if ([string]::IsNullOrWhiteSpace($script:PostgresPassword)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "No PostgreSQL password is available for authentication testing."

        return $false
    }

    if ([string]::IsNullOrWhiteSpace($script:PsqlPath)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql.exe is not available for PostgreSQL authentication testing."

        return $false
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Testing PostgreSQL authentication..."

    $previousPassword = $env:PGPASSWORD

    try {

        $env:PGPASSWORD = $script:PostgresPassword

        & $script:PsqlPath `
            "--host=$PostgresHost" `
            "--port=$PostgresPort" `
            "--username=$PostgresUser" `
            "--dbname=postgres" `
            "--no-password" `
            "--command=SELECT 1;" 2>&1 | Out-Null

        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "PostgreSQL authentication successful."

            return $true
        }

        Write-InstallerLog `
            -Level "WARN" `
            -Message "PostgreSQL authentication failed."

        return $false
    }
    finally {

        if ($null -eq $previousPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $previousPassword
        }
    }
}

# ============================================================
# Create database if missing
# ============================================================

function New-DatabaseIfMissing {

    param(
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Checking database '$DatabaseName'..."

    $previousPassword = $env:PGPASSWORD

    try {

        $env:PGPASSWORD = $script:PostgresPassword

        $query = "SELECT 1 FROM pg_database WHERE datname = '$DatabaseName';"

        $result = & $script:PsqlPath `
            "--host=$PostgresHost" `
            "--port=$PostgresPort" `
            "--username=$PostgresUser" `
            "--dbname=postgres" `
            "--no-password" `
            "--tuples-only" `
            "--no-align" `
            "--command=$query" 2>&1

        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Unable to query PostgreSQL for database '$DatabaseName'."

            Write-InstallerLog `
                -Level "DEBUG" `
                -Message "psql output: $result"

            return $false
        }

        $databaseExists = ($result | Out-String).Trim() -eq "1"

        if ($databaseExists) {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "Database '$DatabaseName' already exists."

            return $true
        }

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Database '$DatabaseName' does not exist. Creating it..."

        $createQuery = 'CREATE DATABASE "' + $DatabaseName + '";'

        & $script:PsqlPath `
            "--host=$PostgresHost" `
            "--port=$PostgresPort" `
            "--username=$PostgresUser" `
            "--dbname=postgres" `
            "--no-password" `
            "--command=$createQuery" 2>&1 | Out-Null

        $createExitCode = $LASTEXITCODE

        if ($createExitCode -ne 0) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Failed to create database '$DatabaseName'."

            return $false
        }

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Database '$DatabaseName' created successfully."

        return $true
    }
    finally {

        if ($null -eq $previousPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $previousPassword
        }
    }
}

# ============================================================
# Write environment variable
# ============================================================

function Write-EnvValue {

    param(
        [string[]]$Lines,
        [string]$Key,
        [string]$Value
    )

    $escapedKey = [regex]::Escape($Key)

    $found = $false

    $updatedLines = foreach ($line in $Lines) {

        if ($line -match "^\s*$escapedKey\s*=") {

            $found = $true

            "$Key=$Value"
        }
        else {

            $line
        }
    }

    if (-not $found) {

        $updatedLines += "$Key=$Value"
    }

    return $updatedLines
}

# ============================================================
# Build PostgreSQL DATABASE_URL
# ============================================================

function Get-PostgresDatabaseUrl {

    param(
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )

    $encodedUser = [System.Uri]::EscapeDataString($PostgresUser)
    $encodedPassword = [System.Uri]::EscapeDataString($script:PostgresPassword)

    return "postgresql://${encodedUser}:${encodedPassword}@${PostgresHost}:${PostgresPort}/${DatabaseName}"
}

# ============================================================
# Write PostgreSQL environment configuration
# ============================================================

function Write-PostgresEnvironment {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Updating backend PostgreSQL environment configuration..."

    try {

        if (-not (Test-Path $BackendRoot)) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Backend directory does not exist: $BackendRoot"

            Exit-WithInstallerCode $PostgresEnvironmentFailureCode
        }

        # ----------------------------------------------------
        # Preserve existing .env
        # ----------------------------------------------------

        $lines = @()

        if (Test-Path $BackendEnvFile) {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "Existing backend .env detected. Preserving existing configuration."

            $content = Get-Content `
                -Path $BackendEnvFile `
                -Raw `
                -ErrorAction Stop

            # Remove UTF-8 BOM if present.
            $content = $content.TrimStart([char]0xFEFF)

            $lines = $content -split "`r?`n"

            # Remove final empty line generated by split.
            if ($lines.Count -gt 0 -and $lines[-1] -eq "") {

                $lines = $lines[0..($lines.Count - 2)]
            }
        }
        else {

            Write-InstallerLog `
                -Level "INFO" `
                -Message "backend/.env does not exist. Creating it."

            $lines = @()
        }

        # ----------------------------------------------------
        # Build URLs
        # ----------------------------------------------------

        $developmentUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $DevelopmentDatabase

        $testUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $TestDatabase

        # ----------------------------------------------------
        # Update only PostgreSQL-related keys.
        # ----------------------------------------------------

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "DATABASE_URL" `
            -Value $developmentUrl

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "TEST_DATABASE_URL" `
            -Value $testUrl

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "POSTGRES_USER" `
            -Value $PostgresUser

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "POSTGRES_PASSWORD" `
            -Value $script:PostgresPassword

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "POSTGRES_HOST" `
            -Value $PostgresHost

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "POSTGRES_PORT" `
            -Value $PostgresPort

        $lines = Write-EnvValue `
            -Lines $lines `
            -Key "POSTGRES_DB" `
            -Value $DevelopmentDatabase

        # ----------------------------------------------------
        # Write UTF-8 WITHOUT BOM
        # ----------------------------------------------------

        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)

        [System.IO.File]::WriteAllText(
            $BackendEnvFile,
            ($lines -join [Environment]::NewLine),
            $utf8NoBom
        )

        # ----------------------------------------------------
        # Synchronize process environment
        # ----------------------------------------------------

        $env:DATABASE_URL = $developmentUrl
        $env:TEST_DATABASE_URL = $testUrl
        $env:POSTGRES_USER = $PostgresUser
        $env:POSTGRES_PASSWORD = $script:PostgresPassword
        $env:POSTGRES_HOST = $PostgresHost
        $env:POSTGRES_PORT = $PostgresPort
        $env:POSTGRES_DB = $DevelopmentDatabase

        Write-InstallerLog `
            -Level "INFO" `
            -Message "PostgreSQL environment configuration written successfully."

        return $true
    }
    catch {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to write PostgreSQL environment configuration: $($_.Exception.Message)"

        Exit-WithInstallerCode $PostgresEnvironmentFailureCode
    }
}

# ============================================================
# Verify PostgreSQL environment configuration
# ============================================================

function Test-PostgresEnvironment {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Verifying PostgreSQL environment configuration..."

    if (-not (Test-Path $BackendEnvFile)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "backend/.env does not exist."

        return $false
    }

    try {

        $content = Get-Content `
            -Path $BackendEnvFile `
            -Raw `
            -ErrorAction Stop

        # ----------------------------------------------------
        # Verify no UTF-8 BOM
        # ----------------------------------------------------

        $bytes = [System.IO.File]::ReadAllBytes($BackendEnvFile)

        if (
            $bytes.Length -ge 3 -and
            $bytes[0] -eq 0xEF -and
            $bytes[1] -eq 0xBB -and
            $bytes[2] -eq 0xBF
        ) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "backend/.env contains a UTF-8 BOM."

            return $false
        }

        # ----------------------------------------------------
        # Expected values
        # ----------------------------------------------------

        $expectedDevelopmentUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $DevelopmentDatabase

        $expectedTestUrl = Get-PostgresDatabaseUrl `
            -DatabaseName $TestDatabase

        $requiredKeys = @(
            "DATABASE_URL",
            "TEST_DATABASE_URL",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB"
        )

        foreach ($key in $requiredKeys) {

            if ($content -notmatch "(?m)^\s*$([regex]::Escape($key))\s*=") {

                Write-InstallerLog `
                    -Level "ERROR" `
                    -Message "Required environment key is missing: $key"

                return $false
            }
        }

        # ----------------------------------------------------
        # Verify exact database URLs
        # ----------------------------------------------------

        if ($content -notmatch "(?m)^DATABASE_URL=$([regex]::Escape($expectedDevelopmentUrl))\s*$") {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "DATABASE_URL does not match the expected SmartFit development database."

            return $false
        }

        if ($content -notmatch "(?m)^TEST_DATABASE_URL=$([regex]::Escape($expectedTestUrl))\s*$") {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "TEST_DATABASE_URL does not match the expected SmartFit test database."

            return $false
        }

        # ----------------------------------------------------
        # Verify process environment
        # ----------------------------------------------------

        if ($env:DATABASE_URL -ne $expectedDevelopmentUrl) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process DATABASE_URL does not match the expected value."

            return $false
        }

        if ($env:TEST_DATABASE_URL -ne $expectedTestUrl) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process TEST_DATABASE_URL does not match the expected value."

            return $false
        }

        if ($env:POSTGRES_USER -ne $PostgresUser) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process POSTGRES_USER does not match the expected value."

            return $false
        }

        if ($env:POSTGRES_PASSWORD -ne $script:PostgresPassword) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process POSTGRES_PASSWORD does not match the configured PostgreSQL password."

            return $false
        }

        if ($env:POSTGRES_HOST -ne $PostgresHost) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process POSTGRES_HOST does not match the expected value."

            return $false
        }

        if ($env:POSTGRES_PORT -ne $PostgresPort) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process POSTGRES_PORT does not match the expected value."

            return $false
        }

        if ($env:POSTGRES_DB -ne $DevelopmentDatabase) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Process POSTGRES_DB does not match the expected value."

            return $false
        }

        Write-InstallerLog `
            -Level "INFO" `
            -Message "PostgreSQL environment configuration verified successfully."

        return $true
    }
    catch {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to verify PostgreSQL environment: $($_.Exception.Message)"

        return $false
    }
}

# ============================================================
# Initialize PostgreSQL
# ============================================================

function Initialize-PostgreSQL {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Initializing PostgreSQL for SmartFit..."

    # --------------------------------------------------------
    # Determine whether PostgreSQL already exists.
    # --------------------------------------------------------

    $postgresExists = Find-PostgreSQL

    if ($postgresExists) {

        $script:PostgresWasPreviouslyInstalled = $true

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Existing PostgreSQL installation detected."

        # ----------------------------------------------------
        # Existing installation:
        # ask for the current password.
        # ----------------------------------------------------

        Request-ExistingPostgresPassword

        if (-not (Test-PostgresAuthentication)) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "The supplied PostgreSQL password is incorrect."

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "The existing PostgreSQL installation was NOT modified."

            Exit-WithInstallerCode $PostgresAuthenticationFailureCode
        }

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Existing PostgreSQL authentication verified."
    }
    else {

        # ----------------------------------------------------
        # Fresh installation.
        # ----------------------------------------------------

        Write-InstallerLog `
            -Level "INFO" `
            -Message "No PostgreSQL installation detected. Starting fresh installation."

        Install-PostgreSQL

        # ----------------------------------------------------
        # Configure SmartFit2026 on the new postgres role.
        # ----------------------------------------------------

        if (-not (Set-NewPostgresPassword)) {

            Write-InstallerLog `
                -Level "ERROR" `
                -Message "Failed to configure PostgreSQL for SmartFit."

            Exit-WithInstallerCode $PostgresAuthenticationFailureCode
        }
    }

    # --------------------------------------------------------
    # Refresh process PATH again after PostgreSQL setup.
    # --------------------------------------------------------

    Initialize-ProcessPath

    # --------------------------------------------------------
    # Ensure PostgreSQL is still discoverable.
    # --------------------------------------------------------

    if (-not (Find-PostgreSQL)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL could not be located after initialization."

        Exit-WithInstallerCode $PostgresInstallFailureCode
    }

    # --------------------------------------------------------
    # Final authentication verification.
    # --------------------------------------------------------

    if (-not (Test-PostgresAuthentication)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL authentication verification failed."

        Exit-WithInstallerCode $PostgresAuthenticationFailureCode
    }

    # --------------------------------------------------------
    # Create development database.
    # --------------------------------------------------------

    if (-not (New-DatabaseIfMissing -DatabaseName $DevelopmentDatabase)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to initialize SmartFit development database."

        Exit-WithInstallerCode $PostgresDatabaseFailureCode
    }

    # --------------------------------------------------------
    # Create test database.
    # --------------------------------------------------------

    if (-not (New-DatabaseIfMissing -DatabaseName $TestDatabase)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to initialize SmartFit test database."

        Exit-WithInstallerCode $PostgresDatabaseFailureCode
    }

    # --------------------------------------------------------
    # Write backend/.env.
    # --------------------------------------------------------

    if (-not (Write-PostgresEnvironment)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to configure backend PostgreSQL environment."

        Exit-WithInstallerCode $PostgresEnvironmentFailureCode
    }

    # --------------------------------------------------------
    # Verify backend/.env.
    # --------------------------------------------------------

    if (-not (Test-PostgresEnvironment)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL environment verification failed."

        Exit-WithInstallerCode $PostgresEnvironmentFailureCode
    }

    # --------------------------------------------------------
    # Final status.
    # --------------------------------------------------------

    Write-InstallerLog `
        -Level "INFO" `
        -Message "PostgreSQL initialization completed successfully."

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Development database: $DevelopmentDatabase"

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Test database: $TestDatabase"

    if ($script:PostgresWasPreviouslyInstalled) {

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Existing PostgreSQL password was preserved."
    }
    else {

        Write-InstallerLog `
            -Level "INFO" `
            -Message "New PostgreSQL postgres role configured with the SmartFit default password."
    }

    return $true
}