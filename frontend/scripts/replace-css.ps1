<#
.SYNOPSIS
    Replaces CSS for a specific UI element and optionally removes
    duplicate element-specific CSS from another stylesheet.

.DESCRIPTION
    This script is designed for the SmartFit frontend CSS polishing
    workflow.

    SmartFit separates CSS responsibilities as follows:

        App.css
            Global application-level styling.

        index.css
            Element and page-specific styling.

    When an element has CSS duplicated across both files, this script
    can:

        1. Replace the element's CSS in the primary stylesheet.
        2. Remove the element's CSS from the cleanup stylesheet.
        3. Create backups before making any changes.
        4. Leave unrelated CSS untouched.

    Example:

        Primary stylesheet:
            frontend/src/index.css

        Cleanup stylesheet:
            frontend/src/App.css

        Element:
            navbar

    Result:

        index.css
            Contains the new Navbar CSS.

        App.css
            No longer contains Navbar-specific CSS.

.PARAMETER TargetFile
    The primary CSS file that should receive the replacement CSS.

.PARAMETER CleanupFiles
    Optional CSS files from which the specified element's CSS
    should be removed.

.PARAMETER Element
    The CSS element to replace/remove.

    Example:
        navbar

.PARAMETER Replacement
    CSS review/replacement file containing the new CSS.

.PARAMETER NoBackup
    Prevents creation of backup files.

    This should normally NOT be used during development.

.EXAMPLE
    .\frontend\scripts\replace-css.ps1 `
        -TargetFile "frontend\src\index.css" `
        -CleanupFiles "frontend\src\App.css" `
        -Element "navbar" `
        -Replacement "frontend\scripts\css-review\navbar-replacement.css"

.NOTES
    Project: SmartFit
    Purpose: Frontend CSS/UI polishing
#>


# ============================================================
# SCRIPT PARAMETERS
# ============================================================

param(

    # --------------------------------------------------------
    # PRIMARY STYLESHEET
    # --------------------------------------------------------
    #
    # This is the stylesheet that receives the new CSS.
    #
    [Parameter(Mandatory = $true)]
    [string]$TargetFile,


    # --------------------------------------------------------
    # CLEANUP STYLESHEETS
    # --------------------------------------------------------
    #
    # These files will have CSS belonging to the specified
    # element removed.
    #
    # This is useful when element-specific CSS has accidentally
    # been placed in a global stylesheet such as App.css.
    #
    [Parameter(Mandatory = $false)]
    [string[]]$CleanupFiles = @(),


    # --------------------------------------------------------
    # ELEMENT
    # --------------------------------------------------------
    #
    # Example:
    #
    #     navbar
    #
    # This targets selectors such as:
    #
    #     .navbar
    #     .navbar-brand
    #     .navbar-links
    #     .navbar-user
    #
    [Parameter(Mandatory = $true)]
    [string]$Element,


    # --------------------------------------------------------
    # REPLACEMENT CSS
    # --------------------------------------------------------
    #
    # File containing the new CSS rules.
    #
    [Parameter(Mandatory = $true)]
    [string]$Replacement,


    # --------------------------------------------------------
    # OPTIONAL BACKUP CONTROL
    # --------------------------------------------------------
    #
    # Backups are created by default.
    #
    # Use -NoBackup only when you deliberately do not want
    # backup files.
    #
    [Parameter(Mandatory = $false)]
    [switch]$NoBackup
)


# ============================================================
# ERROR HANDLING
# ============================================================
#
# Stop execution when an unexpected PowerShell error occurs.
# This prevents the script from silently continuing after
# something has gone wrong.
# ============================================================

$ErrorActionPreference = "Stop"


# ============================================================
# DETERMINE SMARTFIT PROJECT ROOT
# ============================================================
#
# The script is located at:
#
#     SmartFit/
#         frontend/
#             scripts/
#                 replace-css.ps1
#
# Therefore two levels above $PSScriptRoot is:
#
#     SmartFit/
#
# This allows the script to resolve relative paths consistently
# regardless of the directory from which PowerShell executes it.
# ============================================================

$ProjectRoot = [System.IO.Path]::GetFullPath(
    (Join-Path $PSScriptRoot "..\..")
)


# ============================================================
# FUNCTION: RESOLVE PROJECT PATH
# ============================================================
#
# Converts a supplied path into an absolute path.
#
# Absolute paths:
#     Used directly.
#
# Relative paths:
#     Resolved relative to the SmartFit project root.
#
# Example:
#
#     frontend\src\index.css
#
# becomes:
#
#     C:\Users\...\SmartFit\frontend\src\index.css
# ============================================================

function Resolve-ProjectPath {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )


    # If the supplied path is already absolute, return it.
    if ([System.IO.Path]::IsPathRooted($Path)) {

        return [System.IO.Path]::GetFullPath($Path)
    }


    # Otherwise resolve it from the SmartFit project root.
    return [System.IO.Path]::GetFullPath(
        (Join-Path $ProjectRoot $Path)
    )
}


# ============================================================
# FUNCTION: REMOVE CSS COMMENTS
# ============================================================
#
# The replacement file may contain explanatory comments such
# as:
#
#     /* =====================================================
#        SMARTFIT NAVBAR
#        ===================================================== */
#
# These comments are useful during review but do not need to
# be copied into the production stylesheet.
#
# This function removes CSS comments before the replacement
# is inserted.
# ============================================================

function Remove-CssComments {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Content
    )


    return [regex]::Replace(
        $Content,
        "/\*[\s\S]*?\*/",
        ""
    )
}


# ============================================================
# FUNCTION: FIND CSS BLOCKS
# ============================================================
#
# Finds complete CSS rules whose selector contains the
# requested element.
#
# Example:
#
#     Element = navbar
#
# Possible matches:
#
#     .navbar
#     .navbar-brand
#     .navbar-links
#     .navbar-links a
#     .navbar-user
#     .navbar-logout:hover
#
# The parser tracks:
#
#     - CSS braces
#     - CSS comments
#     - quoted strings
#
# This prevents braces inside comments or strings from
# confusing the block detection.
# ============================================================

function Find-CssBlocks {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$Element
    )


    # Escape the requested element before using it in the
    # regular expression.
    $escapedElement = [regex]::Escape($Element)


    # --------------------------------------------------------
    # CSS SELECTOR PATTERN
    # --------------------------------------------------------
    #
    # The pattern searches for selectors containing:
    #
    #     .element
    #
    # and optionally:
    #
    #     -suffix
    #     _suffix
    #
    # Therefore "navbar" can match:
    #
    #     .navbar
    #     .navbar-brand
    #     .navbar-links
    #     .navbar-user
    #
    $pattern =
        "(?m)^[ \t]*[^@\r\n{}]*\.$escapedElement(?:[-_][A-Za-z0-9_-]+)?[^{}\r\n]*\{"


    # Collection used to store discovered CSS blocks.
    $blocks =
        New-Object System.Collections.Generic.List[object]


    # Search the complete CSS content.
    foreach ($match in [regex]::Matches($Content, $pattern)) {

        # Starting character position of the selector.
        $start = $match.Index


        # Find the opening brace belonging to the selector.
        $openBrace = $Content.IndexOf("{", $start)


        # Invalid selector; skip it.
        if ($openBrace -lt 0) {
            continue
        }


        # ----------------------------------------------------
        # CSS PARSING STATE
        # ----------------------------------------------------

        # Current brace depth.
        $depth = 0

        # Whether we are inside a quoted string.
        $inString = $false

        # Stores the type of string quote.
        $stringChar = ""

        # Whether we are inside a CSS comment.
        $inComment = $false

        # Ending position of the CSS block.
        $end = -1


        # ----------------------------------------------------
        # WALK THROUGH THE CSS
        # ----------------------------------------------------

        for ($i = $openBrace; $i -lt $Content.Length; $i++) {

            $char = $Content[$i]


            # Obtain the next character where possible.
            $next = ""

            if ($i + 1 -lt $Content.Length) {
                $next = $Content[$i + 1]
            }


            # ------------------------------------------------
            # HANDLE CSS COMMENTS
            # ------------------------------------------------

            if ($inComment) {

                # Detect the end of:
                #
                #     /* comment */
                #
                if ($char -eq "*" -and $next -eq "/") {

                    $inComment = $false

                    # Skip the slash.
                    $i++
                }

                continue
            }


            # Detect the beginning of a CSS comment.
            if (
                -not $inString -and
                $char -eq "/" -and
                $next -eq "*"
            ) {

                $inComment = $true

                # Skip the asterisk.
                $i++

                continue
            }


            # ------------------------------------------------
            # HANDLE QUOTED STRINGS
            # ------------------------------------------------
            #
            # Example:
            #
            #     content: "{";
            #
            # The brace above belongs to a string and should
            # not be counted as a CSS brace.
            # ------------------------------------------------

            if ($inString) {

                # Handle escaped characters such as:
                #
                #     \"
                #
                if (
                    $char -eq "\" -and
                    $i + 1 -lt $Content.Length
                ) {

                    $i++

                    continue
                }


                # Detect the end of the quoted string.
                if ($char -eq $stringChar) {

                    $inString = $false
                }

                continue
            }


            # Detect the beginning of a quoted string.
            if ($char -eq '"' -or $char -eq "'") {

                $inString = $true

                $stringChar = $char

                continue
            }


            # ------------------------------------------------
            # HANDLE CSS BRACES
            # ------------------------------------------------

            if ($char -eq "{") {

                $depth++
            }
            elseif ($char -eq "}") {

                $depth--


                # When the depth returns to zero, the complete
                # CSS block has been found.
                if ($depth -eq 0) {

                    $end = $i + 1

                    break
                }
            }
        }


        # ----------------------------------------------------
        # SAVE VALID CSS BLOCK
        # ----------------------------------------------------

        if ($end -gt $start) {

            $blocks.Add(
                [PSCustomObject]@{
                    Start = $start

                    End = $end

                    Text = $Content.Substring(
                        $start,
                        $end - $start
                    )
                }
            )
        }
    }


    return $blocks
}


# ============================================================
# FUNCTION: REMOVE CSS BLOCKS
# ============================================================
#
# Removes all CSS blocks belonging to the specified element.
#
# The blocks are removed starting from the bottom of the file.
#
# This is important because removing text from the beginning
# of the document would otherwise change the character
# positions of all blocks appearing later.
# ============================================================

function Remove-CssBlocks {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$Element
    )


    # Find all matching CSS blocks.
    $blocks =
        Find-CssBlocks `
            -Content $Content `
            -Element $Element


    # Nothing to remove.
    if ($blocks.Count -eq 0) {

        return [PSCustomObject]@{
            Content = $Content
            Count = 0
        }
    }


    # Work from the bottom of the stylesheet upward.
    $updatedContent = $Content


    $orderedBlocks =
        $blocks |
        Sort-Object Start -Descending


    foreach ($block in $orderedBlocks) {

        $updatedContent =
            $updatedContent.Remove(
                $block.Start,
                $block.End - $block.Start
            )
    }


    # Reduce excessive blank lines created by removal.
    $updatedContent =
        [regex]::Replace(
            $updatedContent,
            "(\r?\n){3,}",
            "`r`n`r`n"
        )


    return [PSCustomObject]@{
        Content = $updatedContent
        Count = $blocks.Count
    }
}


# ============================================================
# FUNCTION: NEW CSS BACKUP
# ============================================================
#
# Creates a timestamped backup before a CSS file is modified.
#
# "New" is an approved PowerShell verb, which keeps the script
# compatible with PSScriptAnalyzer's PSUseApprovedVerbs rule.
#
# Example:
#
#     index.css
#
# becomes:
#
#     index.css.20260915-221530.bak
# ============================================================

function New-CssBackup {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )


    # Generate a timestamp that is safe to use in a filename.
    $timestamp =
        Get-Date -Format "yyyyMMdd-HHmmss"


    # Build the backup filename.
    $backupPath =
        "$Path.$timestamp.bak"


    # Copy the original file to the backup location.
    Copy-Item `
        -LiteralPath $Path `
        -Destination $backupPath `
        -Force


    return $backupPath
}


# ============================================================
# VALIDATE REPLACEMENT FILE
# ============================================================

$replacementPath =
    Resolve-ProjectPath -Path $Replacement


if (-not (Test-Path -LiteralPath $replacementPath)) {

    throw @"
Replacement CSS file was not found.

Supplied:
$Replacement

Resolved:
$replacementPath
"@
}


# ============================================================
# READ REPLACEMENT CSS
# ============================================================

$replacementContent =
    Get-Content `
        -LiteralPath $replacementPath `
        -Raw


# Remove explanatory CSS comments.
$replacementContent =
    Remove-CssComments -Content $replacementContent


# Remove unnecessary whitespace around the replacement.
$replacementContent =
    $replacementContent.Trim()


# Make sure the replacement contains actual CSS.
if ([string]::IsNullOrWhiteSpace($replacementContent)) {

    throw "The replacement CSS file does not contain usable CSS."
}


# ============================================================
# PROCESS TARGET FILE
# ============================================================
#
# This is the stylesheet that will receive the new CSS.
#
# For the Navbar:
#
#     index.css
#
# is the target file.
# ============================================================

$targetPath =
    Resolve-ProjectPath -Path $TargetFile


# Verify the target exists.
if (-not (Test-Path -LiteralPath $targetPath)) {

    throw @"
Target CSS file was not found.

Supplied:
$TargetFile

Resolved:
$targetPath
"@
}


# Read the existing target stylesheet.
$targetContent =
    Get-Content `
        -LiteralPath $targetPath `
        -Raw
        


# ============================================================
# CREATE TARGET BACKUP
# ============================================================

if (-not $NoBackup) {

    $targetBackup =
        New-CssBackup -Path $targetPath


    Write-Host ""

    Write-Host "Backup created:" `
        -ForegroundColor Yellow

    Write-Host "  $targetBackup"
}


# ============================================================
# REMOVE EXISTING TARGET CSS
# ============================================================
#
# Existing Navbar CSS is removed from index.css before the
# new version is inserted.
#
# This prevents old and new Navbar rules from competing with
# one another.
# ============================================================

$targetResult =
    Remove-CssBlocks `
        -Content $targetContent `
        -Element $Element


$targetContent =
    $targetResult.Content


# ============================================================
# INSERT NEW CSS
# ============================================================
#
# The replacement CSS is appended to the stylesheet.
#
# Appending the new rules keeps the operation predictable and
# avoids accidentally inserting CSS inside another selector.
# ============================================================

$targetContent =
    $targetContent.TrimEnd() +
    "`r`n`r`n" +
    "/* =========================================================" +
    "`r`n" +
    "   SMARTFIT $($Element.ToUpper()) STYLES" +
    "`r`n" +
    "   Managed by replace-css.ps1" +
    "`r`n" +
    "   ========================================================= */" +
    "`r`n`r`n" +
    $replacementContent +
    "`r`n"


# Write the updated target stylesheet.
Set-Content `
    -LiteralPath $targetPath `
    -Value $targetContent `
    -Encoding UTF8


# ============================================================
# PROCESS CLEANUP FILES
# ============================================================
#
# Cleanup files are usually global stylesheets such as App.css.
#
# The requested element's CSS is removed from these files so
# that element-specific styling has one clear owner.
#
# For the Navbar:
#
#     index.css → owns Navbar styling
#
#     App.css   → remains global
# ============================================================

$cleanupResults =
    New-Object System.Collections.Generic.List[object]


foreach ($cleanupFile in $CleanupFiles) {

    # Resolve cleanup stylesheet path.
    $cleanupPath =
        Resolve-ProjectPath -Path $cleanupFile


    # --------------------------------------------------------
    # VERIFY CLEANUP FILE
    # --------------------------------------------------------

    if (-not (Test-Path -LiteralPath $cleanupPath)) {

        Write-Warning @"
Cleanup file not found:

  Supplied : $cleanupFile
  Resolved : $cleanupPath

The file was skipped.
"@

        continue
    }


    # Read the cleanup stylesheet.
    $cleanupContent =
        Get-Content `
            -LiteralPath $cleanupPath `
            -Raw


    # Find element-specific CSS in the cleanup file.
    $cleanupBlocks =
        Find-CssBlocks `
            -Content $cleanupContent `
            -Element $Element


    # --------------------------------------------------------
    # NOTHING TO CLEAN
    # --------------------------------------------------------

    if ($cleanupBlocks.Count -eq 0) {

        $cleanupResults.Add(
            [PSCustomObject]@{
                File = $cleanupFile

                Removed = 0

                Status = "No matching CSS found"
            }
        )

        continue
    }


    # --------------------------------------------------------
    # CREATE CLEANUP BACKUP
    # --------------------------------------------------------

    if (-not $NoBackup) {

        $cleanupBackup =
            New-CssBackup -Path $cleanupPath


        Write-Host ""

        Write-Host "Backup created:" `
            -ForegroundColor Yellow

        Write-Host "  $cleanupBackup"
    }


    # --------------------------------------------------------
    # REMOVE ELEMENT CSS
    # --------------------------------------------------------

    $cleanupResult =
        Remove-CssBlocks `
            -Content $cleanupContent `
            -Element $Element


    # Use the cleaned content to overwrite the cleanup file.
    Set-Content `
        -LiteralPath $cleanupPath `
        -Value $cleanupResult.Content `
        -Encoding UTF8


    # Store information for the final summary.
    $cleanupResults.Add(
        [PSCustomObject]@{
            File = $cleanupFile

            Removed = $cleanupResult.Count

            Status = "Cleaned"
        }
    )
}


# ============================================================
# FINAL SUMMARY
# ============================================================

Write-Host ""

Write-Host "============================================" `
    -ForegroundColor Cyan

Write-Host " CSS REPLACEMENT COMPLETE" `
    -ForegroundColor Green

Write-Host "============================================" `
    -ForegroundColor Cyan

Write-Host ""

Write-Host "Project Root:"
Write-Host "  $ProjectRoot"

Write-Host ""

Write-Host "Element:"
Write-Host "  .$Element"

Write-Host ""

Write-Host "Primary stylesheet:"
Write-Host "  $targetPath"

Write-Host ""

Write-Host "Existing target rules removed:"
Write-Host "  $($targetResult.Count)"

Write-Host ""

Write-Host "New CSS inserted:"
Write-Host "  Yes"

Write-Host ""


# ============================================================
# DISPLAY CLEANUP RESULTS
# ============================================================

if ($CleanupFiles.Count -gt 0) {

    Write-Host "Cleanup results:" `
        -ForegroundColor Cyan


    foreach ($result in $cleanupResults) {

        Write-Host ""

        Write-Host "  File:"
        Write-Host "    $($result.File)"

        Write-Host "  Rules removed:"
        Write-Host "    $($result.Removed)"

        Write-Host "  Status:"
        Write-Host "    $($result.Status)"
    }
}


Write-Host ""


# ============================================================
# DISPLAY BACKUP STATUS
# ============================================================

if ($NoBackup) {

    Write-Host "Backups:"
    Write-Host "  Disabled" `
        -ForegroundColor Red
}
else {

    Write-Host "Backups:"
    Write-Host "  Created before modification" `
        -ForegroundColor Green
}


Write-Host ""


# ============================================================
# COMPLETION MESSAGE
# ============================================================

Write-Host "Original unrelated CSS was preserved." `
    -ForegroundColor Green

Write-Host ""