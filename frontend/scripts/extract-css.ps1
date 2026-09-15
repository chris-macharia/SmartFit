<#
.SYNOPSIS
    Extracts CSS rules related to a specific UI element.

.DESCRIPTION
    This script searches one or more CSS files for selectors containing
    a specified element name and writes the matching CSS rules to a
    separate review file.

    Example:
        .navbar
        .navbar-brand
        .navbar-links
        .navbar-user
        .navbar-logout:hover

    The script is designed for the SmartFit frontend polishing workflow:

        1. Identify a UI element.
        2. Extract its existing CSS.
        3. Review and redesign the styles.
        4. Prepare replacement CSS.
        5. Apply the replacement separately.

    IMPORTANT:
        This script NEVER modifies the original CSS files.

.PARAMETER Files
    One or more CSS files to search.

    Relative paths are resolved relative to the SmartFit project root.

.PARAMETER Element
    The CSS element name to search for.

    Example:
        navbar

    This will match selectors such as:
        .navbar
        .navbar-brand
        .navbar-links
        .navbar-user

.PARAMETER Output
    The file where the extracted CSS will be written.

    Relative paths are resolved relative to the SmartFit project root.

.EXAMPLE
    .\frontend\scripts\extract-css.ps1 `
        -Files "frontend\src\index.css","frontend\src\App.css" `
        -Element "navbar" `
        -Output "frontend\scripts\css-review\navbar.css"

.NOTES
    Project: SmartFit
    Purpose: Frontend CSS/UI polishing
#>


# ============================================================
# SCRIPT PARAMETERS
# ============================================================

param(
    # One or more CSS source files.
    [Parameter(Mandatory = $true)]
    [string[]]$Files,

    # CSS element to search for.
    [Parameter(Mandatory = $true)]
    [string]$Element,

    # Destination file for the extracted CSS.
    [Parameter(Mandatory = $true)]
    [string]$Output
)


# ============================================================
# ERROR HANDLING
# ============================================================
#
# Stop execution when an unexpected PowerShell error occurs.
# This prevents the script from silently continuing with
# incomplete or incorrect data.
# ============================================================

$ErrorActionPreference = "Stop"


# ============================================================
# DETERMINE THE SMARTFIT PROJECT ROOT
# ============================================================
#
# The script is stored at:
#
#   SmartFit/
#       frontend/
#           scripts/
#               extract-css.ps1
#
# Therefore:
#
#   $PSScriptRoot
#       = SmartFit/frontend/scripts
#
# Moving two directories upward gives:
#
#   SmartFit/
#
# This allows the script to work regardless of the directory
# from which PowerShell launches it.
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
# Rules:
#
# 1. Absolute paths are used directly.
#
# 2. Relative paths are resolved relative to the SmartFit
#    project root rather than the current PowerShell directory.
#
# This is important because the script may be executed from:
#
#   SmartFit/
#
# or:
#
#   SmartFit/frontend/
#
# or another directory.
# ============================================================

function Resolve-ProjectPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    # Check whether the supplied path is already absolute.
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    # Otherwise resolve it relative to the SmartFit project root.
    return [System.IO.Path]::GetFullPath(
        (Join-Path $ProjectRoot $Path)
    )
}


# ============================================================
# FUNCTION: FIND CSS BLOCKS
# ============================================================
#
# Searches CSS content for selectors containing the requested
# element name.
#
# For example, when Element = "navbar", this can find:
#
#   .navbar
#   .navbar-brand
#   .navbar-links
#   .navbar-links a
#   .navbar-user
#   .navbar-logout:hover
#
# The function also handles nested CSS braces, comments and
# quoted strings so that the ending brace of a CSS block can
# be identified correctly.
# ============================================================

function Find-CssBlocks {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$Element
    )


    # Escape the element name so that characters in it cannot
    # accidentally become regular-expression operators.
    $escapedElement = [regex]::Escape($Element)


    # --------------------------------------------------------
    # CSS SELECTOR SEARCH PATTERN
    # --------------------------------------------------------
    #
    # We look for selectors containing:
    #
    #   .element
    #
    # followed optionally by:
    #
    #   -brand
    #   -links
    #   -user
    #
    # etc.
    #
    # This allows "navbar" to match:
    #
    #   .navbar
    #   .navbar-brand
    #   .navbar-links
    #
    # but avoids matching unrelated classes that merely happen
    # to contain the word somewhere else.
    # --------------------------------------------------------

    $pattern =
        "(?m)^[ \t]*[^@\r\n{}]*\.$escapedElement(?:[-_][A-Za-z0-9_-]+)?[^{}\r\n]*\{"


    # Collection containing all discovered CSS blocks.
    $blocks = New-Object System.Collections.Generic.List[object]


    # Search the complete CSS document.
    foreach ($match in [regex]::Matches($Content, $pattern)) {

        # Starting position of the selector.
        $start = $match.Index


        # Locate the opening brace of the CSS block.
        $openBrace = $Content.IndexOf("{", $start)


        # If no opening brace is found, skip the match.
        if ($openBrace -lt 0) {
            continue
        }


        # ----------------------------------------------------
        # TRACK CSS BRACE DEPTH
        # ----------------------------------------------------
        #
        # A normal CSS block looks like:
        #
        #   .navbar {
        #       ...
        #   }
        #
        # Some CSS can contain nested structures such as
        # media queries, so we track brace depth rather than
        # simply looking for the next "}".
        # ----------------------------------------------------

        $depth = 0

        # Tracks whether we are currently inside a quoted
        # string.
        $inString = $false

        # Stores whether the current string uses " or '.
        $stringChar = ""

        # Tracks CSS comments:
        #
        #   /* comment */
        #
        $inComment = $false

        # Position where the CSS block ends.
        $end = -1


        # ----------------------------------------------------
        # WALK THROUGH THE CSS CONTENT
        # ----------------------------------------------------

        for ($i = $openBrace; $i -lt $Content.Length; $i++) {

            $char = $Content[$i]


            # Safely obtain the next character.
            $next = ""

            if ($i + 1 -lt $Content.Length) {
                $next = $Content[$i + 1]
            }


            # ------------------------------------------------
            # HANDLE CSS COMMENTS
            # ------------------------------------------------

            if ($inComment) {

                # End of CSS comment.
                if ($char -eq "*" -and $next -eq "/") {
                    $inComment = $false

                    # Skip the "/" character as well.
                    $i++
                }

                continue
            }


            # Start of CSS comment.
            if (
                -not $inString -and
                $char -eq "/" -and
                $next -eq "*"
            ) {
                $inComment = $true

                # Skip the "*" character.
                $i++

                continue
            }


            # ------------------------------------------------
            # HANDLE QUOTED CSS STRINGS
            # ------------------------------------------------
            #
            # Braces inside a string should not be treated as
            # CSS block braces.
            #
            # Example:
            #
            #   content: "{";
            #
            # The "{" above is part of a string.
            # ------------------------------------------------

            if ($inString) {

                # Handle escaped characters such as:
                #
                #   \"
                #
                if (
                    $char -eq "\" -and
                    $i + 1 -lt $Content.Length
                ) {
                    $i++

                    continue
                }


                # End of the current string.
                if ($char -eq $stringChar) {
                    $inString = $false
                }

                continue
            }


            # Start of a quoted string.
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


                # When the depth returns to zero, the original
                # CSS block is complete.
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
                    ).Trim()
                }
            )
        }
    }


    return $blocks
}


# ============================================================
# PREPARE OUTPUT PATH
# ============================================================
#
# Resolve the output path relative to the SmartFit project
# root.
# ============================================================

$outputPath = Resolve-ProjectPath -Path $Output


# Obtain the directory containing the output file.
$outputDirectory = Split-Path -Parent $outputPath


# Create the output directory when it does not already exist.
if (
    $outputDirectory -and
    -not (Test-Path -LiteralPath $outputDirectory)
) {

    New-Item `
        -ItemType Directory `
        -Path $outputDirectory `
        -Force |
        Out-Null
}


# ============================================================
# PREPARE REVIEW FILE
# ============================================================
#
# The output file contains:
#
# - A header explaining its purpose.
# - The source file associated with each extracted section.
# - The matching CSS blocks.
#
# The original CSS files are never modified.
# ============================================================

$sections =
    New-Object System.Collections.Generic.List[string]


$sections.Add(
    "/* ========================================================="
)

$sections.Add(
    "   SMARTFIT CSS REVIEW FILE"
)

$sections.Add(
    "   Element: $Element"
)

$sections.Add("")

$sections.Add(
    "   Generated by extract-css.ps1"
)

$sections.Add("")

$sections.Add(
    "   This file is intended for review/editing."
)

$sections.Add(
    "   Do NOT modify the original CSS files manually"
)

$sections.Add(
    "   while this review is in progress."
)

$sections.Add(
    "   ========================================================= */"
)

$sections.Add("")


# Tracks whether at least one CSS selector was found.
$foundAnything = $false


# Tracks how many source files were successfully scanned.
$filesScanned = 0


# Tracks how many CSS blocks were extracted.
$totalBlocks = 0


# ============================================================
# PROCESS SOURCE CSS FILES
# ============================================================

foreach ($file in $Files) {

    # Resolve the CSS file relative to the SmartFit project root.
    $path = Resolve-ProjectPath -Path $file


    # --------------------------------------------------------
    # CHECK THAT THE FILE EXISTS
    # --------------------------------------------------------

    if (-not (Test-Path -LiteralPath $path)) {

        Write-Warning @"
File not found:
  Supplied : $file
  Resolved : $path
"@

        continue
    }


    # Count this file as successfully scanned.
    $filesScanned++


    # --------------------------------------------------------
    # READ CSS CONTENT
    # --------------------------------------------------------
    #
    # -LiteralPath prevents PowerShell from interpreting special
    # characters in filenames.
    #
    # -Raw reads the entire CSS file as one string, which is
    # necessary for correctly identifying complete CSS blocks.
    # --------------------------------------------------------

    $content = Get-Content `
        -LiteralPath $path `
        -Raw


    # Find selectors containing the requested element.
    $blocks = Find-CssBlocks `
        -Content $content `
        -Element $Element


    # If this file contains no matching selectors, simply move
    # to the next source file.
    if ($blocks.Count -eq 0) {
        continue
    }


    # At least one matching selector has been found.
    $foundAnything = $true


    # --------------------------------------------------------
    # ADD SOURCE FILE HEADER
    # --------------------------------------------------------

    $sections.Add("")

    $sections.Add(
        "/* ========================================================="
    )

    $sections.Add(
        "   SOURCE FILE: $file"
    )

    $sections.Add(
        "   RESOLVED PATH: $path"
    )

    $sections.Add(
        "   ========================================================= */"
    )

    $sections.Add("")


    # --------------------------------------------------------
    # ADD EXTRACTED CSS BLOCKS
    # --------------------------------------------------------

    foreach ($block in $blocks) {

        $sections.Add($block.Text)

        $sections.Add("")

        $totalBlocks++
    }
}


# ============================================================
# VALIDATE EXTRACTION RESULT
# ============================================================
#
# If no matching selector was found in any source file, stop
# and provide a useful error message.
# ============================================================

if (-not $foundAnything) {

    throw @"
No CSS selectors containing '$Element' were found.

Files supplied:
$($Files -join "`r`n")

Project root:
$ProjectRoot

Check that:
1. The CSS files exist.
2. The element name is correct.
3. The selectors contain '.$Element'.
"@
}


# ============================================================
# WRITE REVIEW FILE
# ============================================================
#
# Write the extracted CSS to the requested output location.
#
# UTF-8 encoding is used so that CSS containing Unicode
# characters remains readable.
# ============================================================

Set-Content `
    -LiteralPath $outputPath `
    -Value ($sections -join "`r`n") `
    -Encoding UTF8


# ============================================================
# DISPLAY COMPLETION SUMMARY
# ============================================================

Write-Host ""

Write-Host "============================================" `
    -ForegroundColor Cyan

Write-Host " CSS EXTRACTION COMPLETE" `
    -ForegroundColor Green

Write-Host "============================================" `
    -ForegroundColor Cyan

Write-Host ""

Write-Host "Project Root : $ProjectRoot"

Write-Host "Element      : $Element"

Write-Host "Files Scanned: $filesScanned"

Write-Host "CSS Blocks   : $totalBlocks"

Write-Host "Output       : $outputPath"

Write-Host ""

Write-Host "The original CSS files were not modified." `
    -ForegroundColor Yellow

Write-Host ""