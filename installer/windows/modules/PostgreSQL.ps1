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
#   3. Configure the postgres role password as postgres.
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
#   - postgres is therefore assigned to the PostgreSQL
#     "postgres" role on a NEW installation.
#   - Existing PostgreSQL passwords are never overwritten.
#
# ============================================================

$PostgresWingetId = "PostgreSQL.PostgreSQL.18"

$PostgresUser = "postgres"

# Password used for a NEW PostgreSQL installation.
# Existing installations keep their existing password.
# NOTE: This is also the password written into backend/.env for a
# fresh install, so the app can connect out-of-the-box.
$DefaultPostgresPassword = "postgres"

$PostgresHost = "localhost"
$PostgresPort = "5432"

# The ONLY two database names SmartFit recognizes. Exact case.
# Any database name that does not match one of these exactly is
# a compliance error - see Test-SmartFitDatabaseNamesAreValid
# and Find-ConflictingDatabaseNames.
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
$PostgresWrongPasswordFailureCode = 41

# Number of times the user is asked to re-enter the existing
# PostgreSQL password before setup gives up.
$MaxPostgresPasswordAttempts = 3

# ------------------------------------------------------------
# Module state
# ------------------------------------------------------------

$script:PsqlPath = $null
$script:PostgresPassword = $null
$script:PostgresWasPreviouslyInstalled = $false

# Set to $true only after both SmartFit databases have been
# confirmed to exist. Any downstream process (e.g. a migration or
# table-reset script) should check Test-SmartFitDatabasesReady
# before touching database tables, rather than assuming this
# module already ran successfully.
$script:PostgresDatabasesReady = $false

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

        Write-SetupFailure `
            -Message "winget is not available." `
            -ExitCode $PostgresInstallFailureCode
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

        Write-SetupFailure `
            -Message "PostgreSQL installation failed. winget exit code: $wingetExitCode" `
            -ExitCode $PostgresInstallFailureCode
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

        Write-SetupFailure `
            -Message "PostgreSQL was installed but psql.exe could not be located." `
            -ExitCode $PostgresInstallFailureCode
    }

    # --------------------------------------------------------
    # Mark installation as NEW
    # --------------------------------------------------------

    $script:PostgresWasPreviouslyInstalled = $false

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT assume that postgres is already the PostgreSQL
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

    param(
        [int]$AttemptNumber = 1,
        [int]$MaxAttempts = 1
    )

    if ($AttemptNumber -eq 1) {

        Write-InstallerLog `
            -Level "INFO" `
            -Message "PostgreSQL already exists on this machine."

        Write-Host ""
        Write-Host "PostgreSQL was detected on this machine." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "The existing PostgreSQL password will NOT be changed." -ForegroundColor Yellow
    }
    else {

        Write-Host ""
        Write-Host "That password was not accepted." -ForegroundColor Red
    }

    Write-Host "Please enter the current password for the PostgreSQL '$PostgresUser' role." -ForegroundColor Yellow

    if ($MaxAttempts -gt 1) {

        Write-Host "(Attempt $AttemptNumber of $MaxAttempts)" -ForegroundColor Yellow
    }

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
        -Message "PostgreSQL password supplied by the user (attempt $AttemptNumber of $MaxAttempts)."

    return $true
}

# ============================================================
# Safe SQL literal / identifier escaping
# ============================================================
#
# Used together with Invoke-PostgresSql below. Values are always
# written into a temp .sql file and run via --file, never
# embedded directly into a --command process argument, because
# Windows native-command argument passing can silently drop
# literal double quotes embedded inside a larger argument (this
# previously caused CREATE DATABASE "SmartFit_db" to reach psql
# unquoted and get lowercase-folded to smartfit_db). Escaping is
# still applied defensively, in case a value ever contains a
# quote character of its own.
# ============================================================

function ConvertTo-PostgresLiteral {

    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    return "'" + ($Value -replace "'", "''") + "'"
}

function ConvertTo-PostgresIdentifier {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    return '"' + ($Value -replace '"', '""') + '"'
}

# ============================================================
# Run psql command via a temp .sql file
# ============================================================

function Invoke-PostgresSql {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Sql,

        [string]$Database = "postgres",

        [string]$HostOverride = $PostgresHost,

        [switch]$NoPassword
    )

    if ([string]::IsNullOrWhiteSpace($script:PsqlPath)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql path has not been initialized."

        return [PSCustomObject]@{ Success = $false; ExitCode = -1; Output = $null }
    }

    if (-not $NoPassword -and [string]::IsNullOrWhiteSpace($script:PostgresPassword)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL password has not been initialized."

        return [PSCustomObject]@{ Success = $false; ExitCode = -1; Output = $null }
    }

    $previousPassword = $env:PGPASSWORD

    $tempSqlFile = Join-Path `
        -Path ([System.IO.Path]::GetTempPath()) `
        -ChildPath ([System.IO.Path]::GetRandomFileName() + ".sql")

    try {

        if ($NoPassword) {

            Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        }
        else {

            $env:PGPASSWORD = $script:PostgresPassword
        }

        [System.IO.File]::WriteAllText(
            $tempSqlFile,
            $Sql,
            (New-Object System.Text.UTF8Encoding($false))
        )

        $output = & $script:PsqlPath `
            "--host=$HostOverride" `
            "--port=$PostgresPort" `
            "--username=$PostgresUser" `
            "--dbname=$Database" `
            "--no-password" `
            "--tuples-only" `
            "--no-align" `
            "--file=$tempSqlFile" 2>&1

        $exitCode = $LASTEXITCODE

        return [PSCustomObject]@{
            Success  = ($exitCode -eq 0)
            ExitCode = $exitCode
            Output   = $output
        }
    }
    finally {

        Remove-Item -Path $tempSqlFile -ErrorAction SilentlyContinue

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
            # initialization. Test postgres before failing.
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
    # postgres is assigned to the postgres role.
    # --------------------------------------------------------

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Setting postgres role password to the SmartFit default password..."

    # --------------------------------------------------------
    # NOTE: same class of issue as CREATE DATABASE - the role
    # name is wrapped in literal double quotes for the SQL
    # identifier. Invoke-PostgresSql runs this via a temp .sql
    # file rather than a --command argument. -NoPassword mirrors
    # the passwordless local connection used above, since we
    # don't yet know the role's password. See New-DatabaseIfMissing
    # for the full explanation of the underlying quoting issue.
    # --------------------------------------------------------

    $roleIdentifier = ConvertTo-PostgresIdentifier -Value $PostgresUser
    $passwordLiteral = ConvertTo-PostgresLiteral -Value $DefaultPostgresPassword

    $passwordResult = Invoke-PostgresSql `
        -Sql "ALTER ROLE $roleIdentifier WITH PASSWORD $passwordLiteral;" `
        -Database "postgres" `
        -HostOverride "localhost" `
        -NoPassword

    if (-not $passwordResult.Success) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to configure the postgres role password."

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql output: $($passwordResult.Output | Out-String)"

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

    param(
        [Parameter()]
        [string]$Password = $script:PostgresPassword
    )

    if ([string]::IsNullOrWhiteSpace($Password)) {

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

        $env:PGPASSWORD = $Password

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
# Check whether a database exists (read-only, no side effects)
# ============================================================

function Test-DatabaseExists {

    param(
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )

    $literal = ConvertTo-PostgresLiteral -Value $DatabaseName

    $sql = "SELECT 1 FROM pg_database WHERE datname = $literal;"

    $result = Invoke-PostgresSql -Sql $sql -Database "postgres"

    if (-not $result.Success) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Unable to query PostgreSQL for database '$DatabaseName'."

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql output: $($result.Output | Out-String)"

        return $false
    }

    return (($result.Output | Out-String).Trim() -eq "1")
}

# ============================================================
# Find databases that conflict with an expected SmartFit name
# ============================================================
#
# SmartFit only ever recognizes two exact, case-sensitive
# database names: SmartFit_db and SmartFit_Test_db. Any other
# database name that merely resembles one of these (different
# case, extra/missing whitespace) is NOT the same database to
# PostgreSQL and must never be silently treated as if it were,
# or silently left alongside a newly created correct one - both
# are compliance errors that need a human to resolve.
# ============================================================

function Find-ConflictingDatabaseNames {

    param(
        [Parameter(Mandatory = $true)]
        [string]$DatabaseName
    )

    $literal = ConvertTo-PostgresLiteral -Value $DatabaseName

    $sql = "SELECT datname FROM pg_database WHERE lower(trim(datname)) = lower(trim($literal)) AND datname <> $literal;"

    $result = Invoke-PostgresSql -Sql $sql -Database "postgres"

    if (-not $result.Success) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Unable to check for conflicting database names for '$DatabaseName'."

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql output: $($result.Output | Out-String)"

        # Fail closed: if we can't verify there's no conflict,
        # do not proceed as though there isn't one.
        return @("<unable to verify>")
    }

    $conflicts = ($result.Output | Out-String) -split "`r?`n" |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -ne "" }

    return @($conflicts)
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

    # ----------------------------------------------------------
    # A similarly-named but non-exact database (different case,
    # e.g. smartfit_db instead of SmartFit_db) is logged as a
    # warning, not treated as fatal. It is a DIFFERENT database
    # as far as PostgreSQL is concerned, so it does not block
    # creating the correctly-named one SmartFit actually needs -
    # it's just surfaced so a human can clean it up later if it's
    # leftover cruft.
    # ----------------------------------------------------------

    $conflicts = Find-ConflictingDatabaseNames -DatabaseName $DatabaseName

    if ($conflicts.Count -gt 0) {

        Write-InstallerLog `
            -Level "WARN" `
            -Message "Found database name(s) resembling but not exactly matching '$DatabaseName': $($conflicts -join ', '). SmartFit only uses the exact name '$DatabaseName' - these will be left untouched."
    }

    if (Test-DatabaseExists -DatabaseName $DatabaseName) {

        Write-InstallerLog `
            -Level "INFO" `
            -Message "Database '$DatabaseName' already exists."

        return $true
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Database '$DatabaseName' does not exist. Creating it..."

    # --------------------------------------------------------
    # NOTE: CREATE DATABASE needs a double-quoted, case-
    # preserving identifier (e.g. "SmartFit_db"). Invoke-
    # PostgresSql runs this via a temp .sql file rather than a
    # --command process argument, because Windows native-command
    # argument passing can silently drop a literal double quote
    # embedded inside a larger argument (this previously caused
    # CREATE DATABASE "SmartFit_db" to arrive at psql unquoted
    # and get lowercase-folded to smartfit_db).
    # --------------------------------------------------------

    $identifier = ConvertTo-PostgresIdentifier -Value $DatabaseName

    $createResult = Invoke-PostgresSql -Sql "CREATE DATABASE $identifier;" -Database "postgres"

    if (-not $createResult.Success) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Failed to create database '$DatabaseName'."

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "psql output: $($createResult.Output | Out-String)"

        return $false
    }

    # ----------------------------------------------------
    # Do not trust the CREATE DATABASE exit code alone.
    # Re-query PostgreSQL to confirm the database is
    # actually present before reporting success.
    # ----------------------------------------------------

    if (-not (Test-DatabaseExists -DatabaseName $DatabaseName)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Database '$DatabaseName' was not found after creation."

        return $false
    }

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Database '$DatabaseName' created and confirmed successfully."

    return $true
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

    # Enclosing the foreach expression in @(...) ensures $updatedLines 
    # remains an array rather than auto-unboxing into a single string scalar.
    $updatedLines = @(foreach ($line in $Lines) {

        if ($line -match "^\s*$escapedKey\s*=") {

            $found = $true

            "$Key=$Value"
        }
        else {

            $line
        }
    })

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

            Write-SetupFailure `
                -Message "Backend directory does not exist: $BackendRoot" `
                -ExitCode $PostgresEnvironmentFailureCode
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

        Write-SetupFailure `
            -Message "Failed to write PostgreSQL environment configuration: $($_.Exception.Message)" `
            -ExitCode $PostgresEnvironmentFailureCode
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
# Confirm both SmartFit databases exist
# ============================================================
#
# This is the checkpoint any downstream process MUST use before
# doing anything to database tables (running migrations, seeding
# data, resetting tables, etc.). It does not rely on this module
# having "remembered" that it ran successfully earlier in the
# same process - it re-queries PostgreSQL directly, every time.
# ============================================================

function Test-SmartFitDatabasesReady {

    if ([string]::IsNullOrWhiteSpace($script:PsqlPath) -or
        [string]::IsNullOrWhiteSpace($script:PostgresPassword)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "PostgreSQL has not been initialized in this session. Refusing to confirm database readiness."

        return $false
    }

    $developmentExists = Test-DatabaseExists -DatabaseName $DevelopmentDatabase
    $testExists = Test-DatabaseExists -DatabaseName $TestDatabase

    if (-not $developmentExists) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Development database '$DevelopmentDatabase' does not exist. Table operations must not proceed."
    }

    if (-not $testExists) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Test database '$TestDatabase' does not exist. Table operations must not proceed."
    }

    $script:PostgresDatabasesReady = ($developmentExists -and $testExists)

    return $script:PostgresDatabasesReady
}

# ============================================================
# Verify the database name constants themselves are compliant
# ============================================================
#
# Guards against the constants above ever being edited to
# something other than the two exact, case-sensitive names
# SmartFit requires. This is a hard requirement, not a
# convention - any drift here is treated as a setup error.
# ============================================================

function Test-SmartFitDatabaseNamesAreValid {

    $expectedDevelopmentName = "SmartFit_db"
    $expectedTestName = "SmartFit_Test_db"

    $isValid = $true

    if (-not ($DevelopmentDatabase -ceq $expectedDevelopmentName)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Configured development database name '$DevelopmentDatabase' does not exactly match the required name '$expectedDevelopmentName'."

        $isValid = $false
    }

    if (-not ($TestDatabase -ceq $expectedTestName)) {

        Write-InstallerLog `
            -Level "ERROR" `
            -Message "Configured test database name '$TestDatabase' does not exactly match the required name '$expectedTestName'."

        $isValid = $false
    }

    return $isValid
}

# ============================================================
# Initialize PostgreSQL
# ============================================================

function Initialize-PostgreSQL {

    Write-InstallerLog `
        -Level "INFO" `
        -Message "Initializing PostgreSQL for SmartFit..."

    # --------------------------------------------------------
    # Fail immediately if the required database names have been
    # changed to anything non-compliant, before touching
    # PostgreSQL at all.
    # --------------------------------------------------------

    if (-not (Test-SmartFitDatabaseNamesAreValid)) {

        Write-SetupFailure `
            -Message "SmartFit database naming configuration is not compliant. Expected exactly 'SmartFit_db' and 'SmartFit_Test_db'." `
            -ExitCode $PostgresDatabaseFailureCode
    }

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
        # ask for the current password, retrying up to
        # $MaxPostgresPasswordAttempts times in case of typos
        # before giving up.
        # ----------------------------------------------------

        $authenticated = $false

        for ($attempt = 1; $attempt -le $MaxPostgresPasswordAttempts; $attempt++) {

            Request-ExistingPostgresPassword `
                -AttemptNumber $attempt `
                -MaxAttempts $MaxPostgresPasswordAttempts

            if (Test-PostgresAuthentication) {

                $authenticated = $true
                break
            }

            Write-InstallerLog `
                -Level "WARN" `
                -Message "PostgreSQL authentication failed (attempt $attempt of $MaxPostgresPasswordAttempts)."
        }

        if (-not $authenticated) {

            Write-SetupFailure `
                -Message "Wrong PostgreSQL password: the supplied password was incorrect after $MaxPostgresPasswordAttempts attempts. The existing PostgreSQL installation was NOT modified." `
                -ExitCode $PostgresWrongPasswordFailureCode
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
        # Configure postgres on the new postgres role.
        # ----------------------------------------------------

        if (-not (Set-NewPostgresPassword)) {

            Write-SetupFailure `
                -Message "Failed to configure PostgreSQL for SmartFit." `
                -ExitCode $PostgresAuthenticationFailureCode
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

        Write-SetupFailure `
            -Message "PostgreSQL could not be located after initialization." `
            -ExitCode $PostgresInstallFailureCode
    }

    # --------------------------------------------------------
    # Final authentication verification.
    # --------------------------------------------------------

    if (-not (Test-PostgresAuthentication)) {

        Write-SetupFailure `
            -Message "PostgreSQL authentication verification failed." `
            -ExitCode $PostgresAuthenticationFailureCode
    }

    # --------------------------------------------------------
    # Create development database.
    # --------------------------------------------------------

    if (-not (New-DatabaseIfMissing -DatabaseName $DevelopmentDatabase)) {

        Write-SetupFailure `
            -Message "Failed to initialize SmartFit development database." `
            -ExitCode $PostgresDatabaseFailureCode
    }

    # --------------------------------------------------------
    # Create test database.
    # --------------------------------------------------------

    if (-not (New-DatabaseIfMissing -DatabaseName $TestDatabase)) {

        Write-SetupFailure `
            -Message "Failed to initialize SmartFit test database." `
            -ExitCode $PostgresDatabaseFailureCode
    }

    # --------------------------------------------------------
    # Explicitly confirm both databases exist before doing
    # anything further. Nothing past this point (including
    # any downstream migration/reset step) should run against
    # databases we haven't actually verified are present.
    # --------------------------------------------------------

    if (-not (Test-SmartFitDatabasesReady)) {

        Write-SetupFailure `
            -Message "SmartFit databases could not be confirmed after creation. Aborting before any further steps." `
            -ExitCode $PostgresDatabaseFailureCode
    }

    # --------------------------------------------------------
    # Write backend/.env.
    # --------------------------------------------------------

    if (-not (Write-PostgresEnvironment)) {

        Write-SetupFailure `
            -Message "Failed to configure backend PostgreSQL environment." `
            -ExitCode $PostgresEnvironmentFailureCode
    }

    # --------------------------------------------------------
    # Verify backend/.env.
    # --------------------------------------------------------

    if (-not (Test-PostgresEnvironment)) {

        Write-SetupFailure `
            -Message "PostgreSQL environment verification failed." `
            -ExitCode $PostgresEnvironmentFailureCode
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