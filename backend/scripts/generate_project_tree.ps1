<#
.SYNOPSIS
    Generates a clean directory tree for the SmartFit project.

.DESCRIPTION
    Displays the SmartFit project structure while excluding directories
    that are generated, environment-specific, or too large to be useful
    in project documentation.

    The output is intended for:
    - README documentation
    - Project structure reviews
    - Architecture documentation
    - Quick inspection of the repository structure

    Excluded directories:
    - .git            Git repository internals
    - .pytest_cache   Pytest cache files
    - .venv           Python virtual environment
    - __pycache__     Python bytecode cache
    - node_modules    Frontend dependencies
    - dist            Frontend build output
    - uploads         Runtime-uploaded files

.NOTES
    Project: SmartFit

    Run from the SmartFit repository root:

        .\backend\scripts\generate_project_tree.ps1

    The script displays the project tree up to four levels deep.
#>


# ---------------------------------------------------------------------------
# Directories to exclude
#
# These directories contain generated files, dependencies, runtime data,
# caches, or environment-specific files that should not appear in the
# documented project structure.
# ---------------------------------------------------------------------------

$exclude = @(
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "uploads"
)


# ---------------------------------------------------------------------------
# Function: Show-Tree
#
# Recursively walks through the project directories and prints a clean
# tree-style structure.
#
# Parameters:
#   Path      - Directory currently being processed.
#   Prefix    - Indentation used for nested directories.
#   Depth     - Current recursion depth.
#   MaxDepth  - Maximum depth to display.
#
# ASCII characters are intentionally used instead of Unicode tree
# characters to avoid PowerShell/Windows encoding problems.
# ---------------------------------------------------------------------------

function Show-Tree {
    param(
        [string]$Path,
        [string]$Prefix = "",
        [int]$Depth = 0,
        [int]$MaxDepth = 4
    )

    # Stop recursion when the maximum depth is reached.
    if ($Depth -gt $MaxDepth) {
        return
    }


    # Get the contents of the current directory.
    #
    # Directories are displayed before files to make the structure
    # easier to read.
    $items = Get-ChildItem -LiteralPath $Path |
        Where-Object {
            $exclude -notcontains $_.Name
        } |
        Sort-Object @{
            Expression = { $_.PSIsContainer }
            Descending = $true
        }, Name


    # Process each item in the current directory.
    for ($i = 0; $i -lt $items.Count; $i++) {

        $item = $items[$i]

        # Determine whether this is the final item at the current level.
        $isLast = ($i -eq $items.Count - 1)


        # Use ASCII-only tree characters.
        if ($isLast) {
            $branch = "\-- "
            $childPrefix = "$Prefix    "
        }
        else {
            $branch = "|-- "
            $childPrefix = "$Prefix|   "
        }


        # Display the current item.
        Write-Output "$Prefix$branch$($item.Name)"


        # If the item is a directory, recursively display its contents.
        if ($item.PSIsContainer) {

            Show-Tree `
                -Path $item.FullName `
                -Prefix $childPrefix `
                -Depth ($Depth + 1) `
                -MaxDepth $MaxDepth
        }
    }
}


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

# Display the project root.
Write-Output "SmartFit/"


# Generate the project tree.
#
# MaxDepth = 4 provides enough detail to document the application structure
# without producing an unnecessarily large README tree.
Show-Tree `
    -Path (Get-Location).Path `
    -MaxDepth 4