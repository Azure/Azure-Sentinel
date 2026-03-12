<#
.SYNOPSIS
Executes the V3 PowerShell script provided in this repo for building solutions. However, it disables the noisy output for automation purposes.

.DESCRIPTION
It runs the CreateSolutionV3 silently so that we can keep our output clean for build and deploy statuses.

.PARAMETER SolutionDataFolderPath
Specifies the path to the Data folder for the particular package you are attempting to test.

.OUTPUTS
Creates a new package version zip file in the Package folder, and also updates the other build outputs, like the manifest, test parameters and UI definitions.

.EXAMPLE
PS ./Solutions/Tanium/ci/build-silently.ps1 "./Solutions/Tanium/Data"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$SolutionDataFolderPath
)

# Reject empty or whitespace-only (Mandatory only prevents omitted param)
if ([string]::IsNullOrWhiteSpace($SolutionDataFolderPath)) {
    Write-Error "SolutionDataFolderPath is required."
    exit 1
}

$currentPath = $PWD.Path
# Trim so trailing newline from git (e.g. when run under Task/sh) doesn't break Set-Location
$repoRoot = $(git rev-parse --show-toplevel).ToString().Trim()

# We must change dirs, since the Azure team wrote this script to run at the root
Set-Location $repoRoot

# Pass path that is valid from repo root (absolute if needed), so createSolutionV3.ps1 works when invoked from Task (cwd was ci)
$pathToPass = $SolutionDataFolderPath
if (-not [System.IO.Path]::IsPathRooted($SolutionDataFolderPath)) {
    $pathToPass = (Join-Path -Path $repoRoot -ChildPath ($SolutionDataFolderPath -replace '^\.\/', '' -replace '^\.\\', '')).Replace('\', '/')
}

# createSolutionV3.ps1 catches all errors and only writes "Error occurred in catch..."
# without exiting non-zero, so we detect failure by that message and exit 1 for build.sh.
$output = & {
    . ./Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 $pathToPass
} *>&1

if ($output -match "Error occurred in catch of createSolutionV3 file") {
    exit 1
}

# Don't forget to go back to the original folder
Set-Location $currentPath