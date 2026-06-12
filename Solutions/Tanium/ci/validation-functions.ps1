<#
.SYNOPSIS
Shared validation functions for solution Data folder, manifest, build zip, and Data Connectors.

.DESCRIPTION
Used by set-connector-versions.ps1, get-new-version.ps1, build-silently.ps1, and get-published-version.ps1 to validate solution paths and manifest files consistently.
#>

<#
.SYNOPSIS
Validates the solution Data folder path and ensures the solution manifest (Solution_*.json) exists.

.DESCRIPTION
Resolves the given path to the solution's Data folder, verifies the folder exists, and ensures exactly one Solution_*.json file is present. Exits with an error if the parameter is empty, the folder is missing, or the manifest file is missing or duplicated.

.PARAMETER SolutionDataFolderPath
Path to the solution Data folder (e.g. Solutions/Tanium/Data). May be relative or absolute.
Relative paths are resolved against the current location (Get-Location).

.OUTPUTS
PSCustomObject with DataFolder, SolutionRoot, and SolutionFilePath (full path to the manifest file).
#>
function Resolve-SolutionDataPath {
    param([string]$SolutionDataFolderPath)
    if ([string]::IsNullOrWhiteSpace($SolutionDataFolderPath)) {
        Write-Error "SolutionDataFolderPath is required."
        exit 1
    }
    $pathToTry = $SolutionDataFolderPath -replace '^\.\/', '' -replace '^\.\\', ''
    $dataFolder = $SolutionDataFolderPath
    if (-not [System.IO.Path]::IsPathRooted($SolutionDataFolderPath)) {
        $dataFolder = (Join-Path (Get-Location) $pathToTry).Replace('\', [System.IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path -LiteralPath $dataFolder)) {
            $repoRoot = (git rev-parse --show-toplevel 2>$null).ToString().Trim()
            if ($repoRoot) {
                $fromRepoRoot = (Join-Path $repoRoot $pathToTry).Replace('\', [System.IO.Path]::DirectorySeparatorChar)
                if (Test-Path -LiteralPath $fromRepoRoot) {
                    $dataFolder = $fromRepoRoot
                }
            }
        }
    } else {
        $dataFolder = $dataFolder.Replace('\', [System.IO.Path]::DirectorySeparatorChar)
    }
    if (-not (Test-Path -LiteralPath $dataFolder)) {
        Write-Error "Solution Data folder not found: $dataFolder"
        exit 1
    }
    $dataFolder = (Resolve-Path -LiteralPath $dataFolder).Path
    $solutionRoot = Split-Path -Parent $dataFolder

    $solutionFiles = Get-ChildItem -Path $dataFolder -Filter 'Solution_*.json' -File -ErrorAction SilentlyContinue
    if (-not $solutionFiles -or $solutionFiles.Count -eq 0) {
        Write-Error "No Solution_*.json found in: $dataFolder. Your solution isn't properly configured."
        exit 1
    }
    if ($solutionFiles.Count -gt 1) {
        Write-Error "Multiple Solution_*.json files in Data folder. Your solution isn't properly configured."
        exit 1
    }
    $solutionFilePath = $solutionFiles[0].FullName

    [PSCustomObject]@{
        DataFolder         = $dataFolder
        SolutionRoot       = $solutionRoot
        SolutionFilePath   = $solutionFilePath
    }
}

<#
.SYNOPSIS
Validates the build version parameter and ensures the package zip exists.

.DESCRIPTION
Checks that BuildVersion is non-empty and that the file Package/<BuildVersion>.zip exists under the solution root. Exits with an error if the parameter is missing or the zip is not found.

.PARAMETER SolutionRoot
Full path to the solution root (parent of the Data folder).

.PARAMETER BuildVersion
The build version string used in the zip filename (e.g. 3.3.0).

.OUTPUTS
The full path to the build zip file.
#>
function Assert-BuildZipExists {
    param([string]$SolutionRoot, [string]$BuildVersion)
    if ([string]::IsNullOrWhiteSpace($BuildVersion)) {
        Write-Error "BuildVersion is required."
        exit 1
    }
    $zipPath = Join-Path $SolutionRoot "Package\$BuildVersion.zip"
    if (-not (Test-Path -LiteralPath $zipPath)) {
        Write-Error "Build package not found: $zipPath. Provide a valid -BuildVersion that matches an existing zip."
        exit 1
    }
    $zipPath
}

<#
.SYNOPSIS
Validates the solution manifest's Data Connectors property and the Data Connectors folder.

.DESCRIPTION
Loads the solution manifest and verifies: the "Data Connectors" property exists and is non-empty; the Data Connectors folder exists under the solution root; mainTemplate.json exists in Package; and a fallback version is defined (DataConnectorCCFVersion or Version). Exits with an error if any check fails.

.PARAMETER SolutionPath
Full path to the solution manifest file (Solution_*.json).

.PARAMETER SolutionRoot
Full path to the solution root (parent of the Data folder).

.OUTPUTS
PSCustomObject with ManifestData (parsed manifest), ConnectorPaths, DataConnectorsFolder, MainTemplatePath, and ManifestFallbackVersion.
#>
function Assert-DataConnectorsManifestAndFolder {
    param([string]$SolutionPath, [string]$SolutionRoot)
    $manifestContents = Get-Content -Raw $SolutionPath | ConvertFrom-Json

    if (-not $manifestContents.PSObject.Properties['Data Connectors']) {
        Write-Error "Solution manifest at $SolutionPath has no 'Data Connectors' property. This script should only be run on solutions with data connectors."
        exit 1
    }
    $connectorPaths = @($manifestContents.'Data Connectors')
    if (-not $connectorPaths -or $connectorPaths.Count -eq 0) {
        Write-Error "Solution manifest at $SolutionPath has an empty 'Data Connectors' property. This script should only be run on solutions with data connectors."
        exit 1
    }

    $dataConnectorsFolder = Join-Path $SolutionRoot 'Data Connectors'
    if (-not (Test-Path -LiteralPath $dataConnectorsFolder) -or -not (Test-Path -LiteralPath $dataConnectorsFolder -PathType Container)) {
        Write-Error "No Data Connectors folder found at: $dataConnectorsFolder. This script should only be run on solutions with data connectors."
        exit 1
    }

    $mainTemplatePath = Join-Path $SolutionRoot 'Package\mainTemplate.json'
    if (-not (Test-Path -LiteralPath $mainTemplatePath)) {
        Write-Error "mainTemplate.json not found at: $mainTemplatePath. Your solution isn't properly configured."
        exit 1
    }

    $manifestFallbackVersion = $null
    if (-not [string]::IsNullOrWhiteSpace($manifestContents.DataConnectorCCFVersion)) {
        $manifestFallbackVersion = $manifestContents.DataConnectorCCFVersion.Trim()
    } elseif (-not [string]::IsNullOrWhiteSpace($manifestContents.Version)) {
        $manifestFallbackVersion = $manifestContents.Version.Trim()
    }
    if (-not $manifestFallbackVersion) {
        Write-Error "Solution manifest must contain either 'DataConnectorCCFVersion' or 'Version'. Neither was found in: $SolutionPath"
        exit 1
    }

    [PSCustomObject]@{
        ManifestData             = $manifestContents
        ConnectorPaths           = $connectorPaths
        DataConnectorsFolder     = $dataConnectorsFolder
        MainTemplatePath         = $mainTemplatePath
        ManifestFallbackVersion  = $manifestFallbackVersion
    }
}
